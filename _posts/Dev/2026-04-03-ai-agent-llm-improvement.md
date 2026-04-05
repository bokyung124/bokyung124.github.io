---
title: "사내 온보딩 에이전트에 적용한 16가지 LLM 기술"
last_modified_at: 2026-04-03T17:30:00+00:00
notion_page_id: 33712b31-a8a8-80ea-aa4f-c94c6fb7c13d
layout: post
categories:
  - Dev
tags:
  - "Data Engineering"
  - "dbt"
  - "LLM"
  - "Airflow"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

> 노션과 슬랙 데이터를 기반으로 신규 입사자의 질문에 답변하는 AI 에이전트를 만들었습니다. "문서를 임베딩해서 벡터 검색하면 되는 거 아냐?"라고 생각할 수 있지만, 실제로 쓸 만한 품질을 내려면 그 이후의 가공이 훨씬 중요했습니다. 이 글에서는 단순 RAG 파이프라인(데이터 추출 → 임베딩 → 벡터 적재 → 검색 → 답변 생성) 위에 얹은 기술들을 정리합니다.

---

## 전체 아키텍처

```
사용자 질문 (Slack)
       │
       ▼
  ┌─ 쿼리 분해 ──────────────────────┐
  │  (LLM이 복합 질문을 2-3개로 분해)   │
  └────────────────────────────────┘
       │ sub_query × N
       ▼
  ┌─ 임베딩 → 벡터 검색 ──────────────┐
  │  BigQuery VECTOR_SEARCH (IVF) │
  │  + 메타데이터 Post-filter        │
  │  + 지능형 Fallback              │
  └───────────────────────────────┘
       │ top-K 청크
       ▼
  ┌─ Cross-Encoder 리랭킹 ────────────┐
  │  Discovery Engine Ranking API   │
  └─────────────────────────────────┘
       │ top-N 청크 (재정렬)
       ▼
  ┌─ 컨텍스트 빌드 ─────────────────────┐
  │  청크 + parent_content + 메타데이터  │
  │  + 대화 이력 (멀티턴)                │
  └──────────────────────────────────┘
       │
       ▼
  ┌─ LLM 답변 생성 ─────────────────┐
  │  구조화된 JSON 출력              │
  │  (답변 + 인용 인덱스 + 후속 질문)   │
  └───────────────────────────────┘
       │
       ▼
  인용 추적 → 출처 필터링 → 응답
```

---

## 1. 데이터 전처리: 검색 품질은 청킹에서 결정됩니다

### 1-1. Heading 기반 시맨틱 청킹

대부분의 RAG 튜토리얼은 고정 길이(예: 500토큰)로 텍스트를 자릅니다. 저는 다르게 접근했습니다. 노션 문서는 이미 헤딩으로 구조화되어 있으니, 이 구조를 그대로 살려서 청킹합니다.

```sql
-- mart_notion_chunks.sql
with block_sections as (
    select
        page_id, block_id, block_order, rich_text_markdown, heading_level,
    sum(case when heading_level is not null then 1 else 0 end)
            over (partition by page_id order by block_order) as section_number
    from stg_notion_blocks
    where rich_text_plain is not null
)
```

핵심은 윈도우 함수입니다. `heading_level`이 있는 블록이 나타날 때마다 `section_number`가 증가합니다. 같은 섹션에 속하는 블록들을 모아서 하나의 청크로 만듭니다.

**왜 이게 중요할까요?** "GA4 대시보드 권한 신청"이라는 질문에 대해, 고정 길이 청킹은 "권한 신청 방법"과 "필요한 정보"를 서로 다른 청크로 잘라버릴 수 있습니다. 헤딩 기반 청킹은 "## 권한 신청" 섹션 전체를 하나의 청크로 유지합니다.

### 1-2. 섹션 오버랩 (Sliding Window)

섹션 경계에서 문맥이 끊기는 문제를 해결하기 위해, 이전 섹션의 마지막 500자를 현재 섹션 앞에 붙입니다.

```sql
-- 이전 섹션의 끝 500자를 현재 섹션에 오버랩
sections_with_overlap as (
    select
        page_id, section_number,
        case
            when lag(section_text) over (partition by page_id order by section_number) is not null
            then concat(
                right(lag(section_text) over (...), 500),
                '\n',
                section_text
            )
            else section_text
        end as section_text
    from sections
)
```

이전 섹션에서 "이 작업을 완료한 후"라고 쓰여 있다면, 다음 섹션만 읽었을 때는 "이 작업"이 뭔지 알 수 없습니다. 오버랩이 이 문맥을 보존합니다.

### 1-3. 노션 댓글 통합

노션 문서에는 본문 외에도 댓글에 중요한 정보가 숨어 있습니다. "이 절차 변경됐어요" 같은 인라인 댓글이나, 페이지 레벨의 피드백을 검색 가능하게 만들었습니다.

```sql
-- 인라인 댓글: 해당 섹션의 청크에 병합
concat(
    section_text,
    case when comments_text is not null
         then concat('\n\n[댓글/피드백]\n', comments_text)
         else '' end
) as chunk_text

-- 페이지 레벨 댓글: 별도 청크로 생성 (section_number=999)
concat('[페이지 댓글]\n', pc.comments_text) as chunk_text
```

### 1-4. 재귀 CTE로 페이지 계층 자동 분류

노션의 페이지 트리를 재귀 CTE로 탐색하면서 세 가지를 동시에 처리합니다:

- **Breadcrumb 경로**: `"마케팅 > SEO > 리포트 가이드"`

- **카테고리 자동 분류**: 최상위 페이지 제목으로 marketing/tech/tools 판별

- **온보딩 마크**: 페이지나 상위 페이지에 "온보딩" 키워드가 있으면 자동 태깅

```sql
with recursive page_hierarchy as (
    -- 앵커: 팀스페이스 직속 페이지 (depth=0)
    select
        page_id, page_title, parent_id,
        page_title as breadcrumb_path,
        0 as depth,
        case
            when lower(page_title) like '%마케팅%' then 'marketing'
            when lower(page_title) = 'NNT Tech' then 'tech'
            ...
        end as category,
        case
            when lower(page_title) like '%온보딩%' then true
            else false
        end as is_onboarding
    from stg_notion_pages
    where parent_type = 'workspace'

    union all

    -- 재귀: 자식 페이지는 부모의 카테고리를 상속
    select
        child.page_id,
        concat(parent.breadcrumb_path, ' > ', child.page_title),
        parent.depth + 1,
        parent.category,  -- 부모 카테고리 상속
        case
            when parent.is_onboarding then true  -- 부모가 온보딩이면 자식도
            when lower(child.page_title) like '%온보딩%' then true
            else false
        end as is_onboarding
    from stg_notion_pages child
    inner join page_hierarchy parent on child.parent_id = parent.page_id
)
```

이 결과는 벡터 검색의 post-filter와 LLM 컨텍스트의 경로 표시에 모두 사용됩니다. 수동 태깅 없이 문서 구조에서 자동으로 메타데이터를 추출하는 것이 핵심입니다.

### 1-5. 슬랙 스레드 기반 청킹

슬랙 메시지는 개별 메시지가 아니라 스레드 단위로 묶어야 의미가 있습니다. "이거 어떻게 해요?" — "이렇게 하면 됩니다" — "감사합니다"가 하나의 검색 단위가 되어야 합니다.

```sql
with thread_groups as (
    select
        coalesce(thread_ts, ts) as thread_id,  -- 단독 메시지도 스레드로 취급
        string_agg(
            concat('[', user_name, '] ', text),
            '\n' order by message_at asc
        ) as thread_text
    from stg_slack_messages
    group by coalesce(thread_ts, ts), channel_id, channel_name
)
```

노션 청크와 슬랙 청크는 최종적으로 `mart_enterprise_chunks` UNION 뷰로 통합되어, 하나의 벡터 검색으로 두 소스를 동시에 탐색합니다.

---

## 2. 검색 파이프라인: 벡터 검색만으로는 부족합니다

### 2-1. 쿼리 분해 (Query Decomposition)

"신규 고객사 세팅 절차가 어떻게 되고, 슬랙 채널은 누가 만들어?" 같은 복합 질문은 하나의 임베딩으로 검색하면 둘 다 놓칩니다. LLM이 먼저 질문을 분석합니다.

```python
class _DecomposeResult(PydanticBaseModel):
    needs_decomposition: bool
    sub_queries: list[str]

async def decompose_query(self, query: str, max_sub_queries: int = 3) -> list[str]:
    response = await loop.run_in_executor(
        None,
        partial(
            self._client.models.generate_content,
            model=self._model,
            contents=f"다음 질문을 분석하세요:\n{query}",
            config=types.GenerateContentConfig(
                system_instruction=DECOMPOSE_SYSTEM_PROMPT,
                temperature=0.1,  # 보수적으로
                response_mime_type="application/json",
                response_schema=_DecomposeResult,
            ),
        ),
    )
```

단순 질문은 `needs_decomposition=false`로 그대로 통과하고, 복합 질문만 분해됩니다. 분해된 각 서브쿼리는 독립적으로 임베딩 → 벡터 검색을 수행하고, 결과를 합쳐서 중복 제거 후 리랭킹합니다.

### 2-2. Cross-Encoder 리랭킹

벡터 검색은 Bi-Encoder 방식이라 빠르지만, 쿼리와 문서 사이의 미세한 의미 차이를 놓칠 수 있습니다. 벡터 검색으로 후보군(top-50)을 뽑은 후, Cross-Encoder 모델로 재정렬하여 최종 top-8을 선정합니다.

```python
class RerankerService:
    async def rerank(self, query: str, chunks: list[ChunkResult], top_n: int = 8):
        records = [
            discoveryengine.RankingRecord(
                id=str(i),
                title=chunk.page_title or "",
                content=chunk.content,
            )
            for i, chunk in enumerate(chunks)
        ]

        rank_request = discoveryengine.RankRequest(
            ranking_config=self._ranking_config,
            model="semantic-ranker-default@latest",
            query=query,
            records=records,
            top_n=top_n,
        )

        response = await loop.run_in_executor(
            None, partial(self._client.rank, request=rank_request)
        )
        # response.records는 score 내림차순으로 정렬되어 반환
        return [chunks[int(record.id)] for record in response.records]
```

Google Discovery Engine의 `semantic-ranker-default@latest` 모델을 사용했습니다. Bi-Encoder(벡터 검색)가 "대충 비슷한 문서"를 빠르게 찾아주면, Cross-Encoder(리랭커)가 "진짜 관련 있는 문서"를 정밀하게 골라줍니다.

### 2-3. 동적 메타데이터 필터링

BigQuery VECTOR_SEARCH의 post-filter로 카테고리, 온보딩 여부, 고객사, 태그를 필터링합니다. 핵심 트릭은 카테고리 필터 시 `top_k`를 3배로 늘리는 것입니다.

```python
# 카테고리 필터 시 post-filter로 걸러지므로 top_k를 넉넉히 확보
default_top_k = self._settings.search_top_k  # 50
if category != "all":
    default_top_k = default_top_k * 3  # 150
```

벡터 검색은 먼저 top-K를 가져온 후 post-filter를 적용하기 때문에, 특정 카테고리만 필터링하면 결과가 부족해질 수 있습니다. top_k를 넉넉히 잡아서 이 손실을 보정합니다.

### 2-4. 지능형 Fallback

검색 결과가 0건이면 필터를 단계적으로 완화합니다:

```
1차: is_onboarding=True + category 필터
     ↓ 0건
2차: is_onboarding 제거 + category 유지
     ↓ 0건
3차: category도 "all"로 확장
```

```python
# 2-a. Fallback: is_onboarding=True에서 0건이면 is_onboarding=False로 재검색
if not chunks and is_onboarding:
    chunks = await self._vector_search.search(
        embedding, request.category,
        is_onboarding=False,  # 온보딩 필터 제거
    )
```

"관련 문서를 찾지 못했습니다"를 최소화하기 위한 장치입니다. 온보딩 전용 문서에 없더라도 일반 문서에서 관련 내용을 찾아줄 수 있습니다.

---

## 3. LLM 답변 생성: 프롬프트 엔지니어링의 디테일

### 3-1. 구조화된 JSON 출력

LLM의 출력을 자유 텍스트가 아닌, Pydantic 스키마로 강제합니다.

```python
class _LLMResult(PydanticBaseModel):
    answer: str                         # Slack mrkdwn 형식의 답변
    cited_indices: list[int]            # 실제 인용한 [출처 N] 번호 (1-based)
    follow_up_questions: list[str]      # 후속 질문 2-3개

response = await loop.run_in_executor(
    None,
    partial(
        self._client.models.generate_content,
        model=self._model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=_LLMResult,  # Gemini JSON mode
        ),
    ),
)
result = response.parsed  # Pydantic 객체로 자동 파싱
```

이렇게 하면 세 가지를 한 번의 LLM 호출로 동시에 얻습니다:

- **답변**: Slack mrkdwn 형식으로 즉시 게시 가능

- **인용 인덱스**: 실제 참조한 출처만 필터링

- **후속 질문**: 대화를 이어갈 수 있는 구체적인 질문

### 3-2. 인용 추적 (Citation Tracking)

LLM이 반환한 `cited_indices`를 기반으로, 실제로 인용된 출처만 사용자에게 보여줍니다.

```python
# 실제 인용된 청크만 sources에 포함
if cited_indices:
    cited_chunks = [chunks[i - 1] for i in cited_indices if 1 <= i <= len(chunks)]
else:
    cited_chunks = chunks[:3]  # fallback: 상위 3개만 노출
sources = self._deduplicate_sources(cited_chunks)
```

"출처 8개를 넘겼지만 LLM이 실제로 참고한 건 3개"인 경우, 나머지 5개를 보여줘봤자 사용자에게 노이즈입니다. `cited_indices`로 LLM이 어떤 출처를 실제로 사용했는지 추적하고, 그것만 보여줍니다.

### 3-3. 질문 유형별 프롬프트 분기

일반 질문과 온보딩 질문은 다른 시스템 프롬프트를 사용합니다.

```python
system_prompt = ONBOARDING_SYSTEM_PROMPT if is_onboarding else SYSTEM_PROMPT
parent_limit = 3500 if is_onboarding else 1500
```

온보딩 질문은 "GA4 접근 권한 신청"의 구체적인 단계, 필요한 정보, 주의사항까지 빠짐없이 전달해야 하므로 더 긴 컨텍스트를 허용합니다.

### 3-4. Parent Content 주입

청크 단위의 컨텍스트만으로는 부족할 때가 있습니다. 각 청크에 해당 페이지의 전체 내용(`parent_content`)도 함께 제공합니다.

```python
def _build_context(self, chunks, *, is_onboarding=False):
    parent_limit = 3500 if is_onboarding else 1500
    for i, chunk in enumerate(chunks, 1):
        header = f"[출처 {i}] (문서: {chunk.page_title}, 경로: {chunk.breadcrumb})"
        if chunk.parent_content:
            content = (
                f"[관련 섹션]\n{chunk.content}\n\n"
                f"[참고: 전체 페이지]\n{chunk.parent_content[:parent_limit]}"
            )
        else:
            content = chunk.content
```

LLM이 "[관련 섹션]"에서 직접적인 답변을 찾되, "[참고: 전체 페이지]"에서 추가 맥락을 얻을 수 있습니다. "이 단계 이후에는..."이라는 표현의 "이 단계"가 뭔지를 전체 페이지에서 파악하는 식입니다.

### 3-5. 후속 질문 추천

매 답변에 2-3개의 후속 질문을 자동 생성합니다. 시스템 프롬프트에서 "현재 컨텍스트에서 파생되는 구체적인 질문"을 요구하고, Slack에서는 클릭 가능한 버튼으로 렌더링합니다.

```
사용자: "크롤링 요청은 어떤 절차로 진행되나요?"
봇: (답변) ...
    [후속 질문]
    🔘 크롤링 결과는 어디서 확인하나요?
    🔘 긴급 크롤링 요청도 같은 절차인가요?
```

사용자가 버튼을 클릭하면 해당 질문으로 자동 재검색되고, 대화 이력이 유지됩니다.

---

## 4. 멀티턴 대화: 스레드 기반 문맥 유지

Slack 스레드를 대화 세션으로 활용합니다. `channel_id + thread_ts` 조합을 키로, 최대 5턴의 대화 이력을 TTL 캐시에 보관합니다.

```python
class ConversationCache:
    def append(self, channel: str, thread_ts: str, query: str, answer: str):
        turns = self._cache.get(key, [])
        turns.append(ConversationTurn(role="user", content=query))
        turns.append(ConversationTurn(role="assistant", content=answer))
        # 최대 턴 수 유지 (FIFO)
        if len(turns) > self._max_turns * 2:
            turns = turns[-(self._max_turns * 2):]
```

LLM 프롬프트에는 이전 대화가 자연스럽게 삽입됩니다:

```
이전 대화:
사용자: 신규 고객사 세팅 절차가 어떻게 돼?
봇: 고객사 세팅은 PM이 노션에 프로젝트 페이지를 생성하고...

현재 질문: 슬랙 채널은 누가 만들어?
```

대화 이력이 있으면 검색 결과 캐시를 우회합니다. 같은 질문이라도 이전 대화에 따라 답변이 달라질 수 있기 때문입니다.

---

## 5. 온보딩 체크리스트 자동 생성

단순 Q&A를 넘어, 카테고리별 학습 경로를 LLM이 자동으로 설계합니다.

```python
async def generate_checklist(self, category: str):
    # 1. 합성 쿼리로 해당 분야의 온보딩 문서를 광범위하게 검색
    embedding = await loop.run_in_executor(
        None, partial(self._embedder.embed_query, f"{cat_name} 온보딩 전체 가이드")
    )

    # 2. 넓은 범위 검색 (top_k=80, result_limit=15)
    chunks = await self._vector_search.search(
        embedding, category, is_onboarding=True, top_k=80, result_limit=15,
    )

    # 3. LLM이 문서들을 분석하여 5-10단계 학습 경로 생성
    title, steps = await self._llm.generate_checklist(category, chunks)
```

LLM의 출력은 구조화된 JSON으로 강제됩니다:

```python
class _ChecklistStep(PydanticBaseModel):
    step_number: int
    title: str            # "SEO 기초 이해하기"
    description: str      # 2-3문장 설명
    search_query: str     # 이 단계의 상세 내용을 검색할 쿼리

class _ChecklistResult(PydanticBaseModel):
    title: str            # "SEO 팀 온보딩 7단계"
    steps: list[_ChecklistStep]
```

각 단계의 `search_query`는 클릭 가능한 버튼으로 제공되어, 해당 단계의 상세 정보를 바로 검색할 수 있습니다. 체크리스트 자체는 24시간 TTL로 캐싱합니다.

---

## 6. 인프라 최적화: 비용과 성능

### 6-1. 증분 임베딩

전체 문서를 매번 재임베딩하는 대신, 변경된 청크만 감지하여 임베딩합니다.

```python
def detect_changed_chunks(bq_client, project_id, dataset):
    query = """
    SELECT c.*
    FROM mart_enterprise_chunks c
    LEFT JOIN mart_enterprise_vectors v ON c.chunk_id = v.chunk_id
    WHERE v.chunk_id IS NULL              -- 신규
       OR c.last_edited_at > v._embedded_at  -- 변경
    """
```

벡터 적재는 MERGE(upsert) 패턴으로 처리합니다:

```sql
MERGE vectors T
USING staging S ON T.chunk_id = S.chunk_id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...
```

문서 1,000개 중 10개가 바뀌었다면, 10개만 임베딩하고 나머지는 건드리지 않습니다. Gemini 임베딩 API 비용과 BigQuery 처리 비용을 모두 절감합니다.

### 6-2. IVF 벡터 인덱스

BigQuery VECTOR_SEARCH의 IVF(Inverted File) 인덱스를 자동 생성하고 관리합니다.

```sql
CREATE VECTOR INDEX IF NOT EXISTS idx_enterprise_vectors_embedding
ON mart_enterprise_vectors(embedding)
STORING (category, is_onboarding, client_name, tags)
OPTIONS (
    index_type = 'IVF',
    distance_type = 'COSINE',
    ivf_options = '{"num_lists": 100}'
)
```

`STORING` 절에 필터링에 사용하는 컬럼들을 포함시켜, post-filter 성능을 최적화합니다. `fraction_lists_to_search` 파라미터로 검색 범위(recall)와 속도 사이의 트레이드오프를 조절합니다.