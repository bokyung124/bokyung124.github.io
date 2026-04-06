---
title: "[dbt] **사내 RAG 기반 챗봇 -** dbt 적용 사례"
last_modified_at: 2026-04-06T13:09:00+00:00
notion_page_id: 33a12b31-a8a8-803b-afe3-d7f1a0659af7
layout: post
categories:
  - Data Engineering
tags:
  - "Data Engineering"
  - "dbt"
  - "SQL"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

## dbt

![image](/assets/img/image.png)

- 데이터 모델링과 변환 로직을 코드로 정의
  - 이미 적재되어있는 데이터를 조회하고 수정하는 데에 최적화된 도구 (EL**T**)

- 변환 흐름을 자동화, 문서화하며 테스트 가능한 구조로 유지하게 도와주는 데이터 엔지니어링 툴

- DW 기반의 분석 환경을 체계적으로 운영하고자 할 때 사용

- 기존 프로젝트에서는 BigQuery에서 View Table 또는 Scheduled Query로 데이터 가공을 스케줄링했는데, dbt를 이용하면 쿼리를 관리하기 더 쉬울 것 같다는 생각이 들었음

### 특징 (장점)

- SQL 기반 

- 버전 관리, CI/CD 등을 도입할 수 있어 코드 관리, 협업, 변경 사항 추적이 가능함

- Jinja 템플릿 엔진 사용 (IF/ELSE, FOR, 변수 사용 등) → 코드 재사용성 극대화
  - `{{ ref('stg_notion_pages') }}` — 모델 참조

  - `{{ source('raw_notion', 'raw_notion_pages') }}` — 소스 참조

  - `{{ env_var('GCP_PROJECT_ID') }}` — 환경변수 주입

  - `{{ config(...) }}` — 모델별 materialization 설정

- 강력한 의존성 관리 (Lineage)
  - `ref()` 함수를 사용하면 테이블 간 관계를 dbt가 스스로 파악함 → DAG 형태의 리니지로 보여줌

- NULL값 여부 확인, 중복값 확인, 참조 무결성 등의 테스트를 간단하게 자동화할 수 있음 → 데이터 신뢰성 보장

- 코드, 테이블에 대한 설명, 데이터 흐름도(DAG)를 깔끔한 문서로 자동 생성해줌

## 프로젝트 아키텍처

```yaml
Notion API ─→ [Airflow: Extract] ─→ BigQuery Raw (notion)
Slack  API ─→ [Airflow: Extract] ─→ BigQuery Raw (slack)
                                        ↓
                              [dbt: Transform]
                                        ↓
                    BigQuery Mart (notion_chunks + slack_chunks)
                                        ↓
                        mart_enterprise_chunks (UNION view)
                                        ↓
                    [Airflow: Embed (Gemini)] → mart_enterprise_vectors
                                        ↓
                        [FastAPI + Gemini] → 사용자 응답
```

## dbt 구조

### Stage 1: Staging (View, 병렬 실행)

- raw 테이블에서 직접 읽기 때문에 모두 동시 실행 가능

- 역할
  - 중복 제거

  - 불필요한 데이터 필터링
    - 노션
      - 아카이브된 페이지 제외

      - 비텍스트 블록 제외

      - 빈 댓글 제외

    - 슬랙
      - 유저 목록에서 슬랙봇 제외

  - 타입 캐스팅 & 정규화

  - 컬럼 선택 & rename

- raw와 나머지 레이어 사이의 계약! 
  - raw 스키마가 변경되어도 staging만 수정하면 intermediate/mart는 영향 없이 유지됨

### Stage 2: Intermediate (Table, 병렬 실행)

- Notion과 Slack 브랜치가 독립적으로 병렬 실행

### Stage 3: Mart (Table, 순차 의존)

```sql
int_notion_page_breadcrumbs ─┐
int_notion_page_content ─────┼─→ mart_notion_documents ─┐
int_notion_db_properties ────┘                          │
                                  stg_notion_blocks ────┼─→ mart_notion_chunks
                                  stg_notion_comments ──┘

int_slack_threads ──────────────┐
int_slack_channel_categories ───┴─→ mart_slack_chunks
```

- `mart_notion_documents`: breadcrumbs + content + properties JOIN → 페이지 완성

- `mart_notion_chunks` : documents에 의존
  - heading 기반 섹션 분할로 청크 생성

  - 각 청크에 breadcrumb + 메타데이터 컨텍스트 주입

  - 블록별 인라인 댓글은 해당 섹션에 삽입, 페이지 레벨 댓글은 별도 청크로 생성

- `mart_slack_chunks` : documents와 독립, 병렬 처리 가능
  - 슬랙 스레드 기반 청크 생성 (1 thread = 1 chunk)

### Stage 4: Enterprise 통합 (View)

```sql
mart_notion_chunks ──┐
                     ├─→ mart_enterprise_chunks (UNION ALL)
mart_slack_chunks ───┘
```

- 노션 + 슬랙 데이터 결합 → 임베딩 파이프라인이 이 view를 읽어 벡터를 생성함

## materialization 선택 근거

- 연산이 가볍거나, 단순 참조이면 view

- 무거운 연산이거나, 여러 곳에서 참조되면 table

- BigQuery에서는 특히 view 체이닝에 따른 스캔 비용을 고려해야 함!

### Staging: View

- **변환이 가벼움** - 중복 제거 + 필터링 + 타입 캐스팅 정도여서 매번 계산해도 부담 없음

- **저장 비용 0** - raw 데이터를 그대로 복제하면 이중 저장이 됨

- **항상 최신** - raw 테이블이 업데이트되면 view가 자동 반영

### Intermediate / Mart: Table

- **무거운 연산** - 재귀 CTE, STRING_AGG 등은 매번 실행하면 비효율적임

- **여러 곳에서 참조** - mart_notion_documents가 intermediate 3개를 JOIN하고, mart_notion_chunks가 다시 documents를 참조함. view면 참조할 때마다 재계산이 체이닝됨

- **BigQuery 비용 구조** - BigQuery는 스캔량 기준 과금 → view 체이닝이 깊어지면 하위 모든 raw 테이블을 매번 풀스캔하게 됨 → table로 물리화하면 이미 계산된 결과만 읽음

### Enterprise Chunk: View

- **단순 UNION ALL** - 변환 로직이 없고, notion + slack 두 테이블을 합치기만 함

- **이미 물리화된 table을 읽음** - 양쪽 chunks가 table이라 추가 비용이 거의 없음

- **저장 절약** - 같은 데이터를 한 번 더 저장할 이유가 없음

## yml 파일의 용도

- dbt에서 `.yml` 파일은 모델의 메타데이터를 정의하는 설정 파일

- 데이터를 어디에서 읽고, 어떤 규칙을 지키고, 어떻게 설명할지 정의
  - SQL에는 비즈니스 로직만 남기고, 메타데이터/테스트/문서는 YML로 분리하는 것이 dbt 컨벤션!

### 1. Sources 정의 (외부 데이터 소스)

```yaml
sources:
  - name: raw_notion
    database: "{{ env_var('GCP_PROJECT_ID') }}"
    schema: onboarding_agent
    tables:
      - name: raw_notion_pages
```

- dbt가 관리하지 않는 외부 테이블 등록

- SQL에서 `{{ source('raw_notion', 'raw_notion_pages') }}` 로 참조할 수 있음 + lineage 추적

### 2. Models 문서화

```yaml
models:
	- name: stg_notion_pages
		description: 페이지 메타데이터 정제 (최신 레코드, 타입 캐스팅)
```

- 각 모델과 컬럼에 description을 달아서 `dbt docs generate` 으로 문서를 자동 생성할 수 있음

### 3. Tests 정의 (데이터 품질 검증)

```yaml
columns: 
	- name: page_id
		tests:
			- unique
			- not_null
```

- `dbt test` 실행 시 컬럼 단위 데이터 품질 테스트 수행
  - `unique`: 중복이 없는지

  - `not_null` : NULL 값이 없는지

## `source()` vs. `ref()`

- staging 모델은 `source()` 로 raw 테이블을 읽고, 그 이후 레이어 (intermediate, mart)는 `ref()` 로 dbt 모델끼리 참조함

- dbt가 DAG 의존 관계를 명확히 파악하고 실행 순서를 결정할 수 있음

## 멱등성 유지

### 1. Staging에서 `ROW_NUMBER` 중복 제거

- 모든 staging 모델에 동일한 패턴이 적용되어 있음
  - 모델 별로 `PARTITION BY` 키는 다름

```sql
deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY block_id
            ORDER BY _extracted_at DESC
        ) AS _rn
    FROM source
),
...
WHERE _rn=1
```

- Airflow가 같은 데이터를 여러 번 적재해도, `_extracted_at` 기준 최신 레코드 1건만 남김

### 2. 전체 Full Refresh (Table) 전략

- intermediate, mart 모델이 모두 `materialized: table`

- incremental 모델이 없음 
  - `is_incremental()`, `unique_key`, merge 전략 없음

- 매 실행 시 테이블을 통째로 다시 생성 → `dbt run`을 여러 번 돌려도 결과가 항상 같음
  - 데이터가 커지면 매번 전체 재생성 비용이 늘어남
    - mart 레이어에 `incremental` + `unique_key` 전략을 도입할 수 있음

### **현재 구조에서 Full Refresh 전략을 사용한 이유**

- 데이터 규모가 작음
  - 사내 노션 + 슬랙 데이터이기 때문에 raw 테이블 자체가 수십만 건 수준 → full refresh 비용이 충분히 감당 가능함

- Append-only 적재 구조와의 충돌
  - Airflow가 raw 테이블에 **append 방식**으로 적재 → 같은 `page_id` 가 추출 시점마다 반복 적재되기 때문에 staging에서 ROW_NUMBER 중복 제거가 필수적임

  - incremental 모델로 바꾸면:
    - `unique_key`로 merge해야 하는데, 이미 staging view가 중복 제거를 하고 있어서 이중 작업이 됨

    - raw 테이블에 늦게 들어온 데이터가 incremental 범위 밖이면 누락 위험 (late-arriving data)

    - `--full-refresh` 를 주기적으로 돌려야 하는 운영 부담 추가

- 노션 데이터의 특성
  - 노션 페이지는 언제든 과거 데이터가 수정될 수 있음

  - incremental은 보통 시점 기반으로 필터링하는데, 이러면
    - 과거에 수정된 페이지의 breadcrumb/content 변경을 놓칠 수 있음

    - 부모 페이지가 바뀌면 자식들의 breadcrumb도 전부 갱신해야 하는데, incremental로는 감지 어려움

### 검증: `dbt test`

- _staging.yml 에 `unique` + `not_null` 테스트가 걸려있어서, 중복 제거가 제대로 됐는지 `dbt test`로 확인할 수 있음

## 청킹 전략 - RAG 파이프라인의 핵심