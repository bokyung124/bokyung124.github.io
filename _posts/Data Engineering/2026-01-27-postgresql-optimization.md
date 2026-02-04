---
title: "**PostgreSQL 쿼리 성능 20배 개선하기 (Part 1) - 문제 정의와 성능 분석**"
last_modified_at: 2026-02-04T05:32:00+00:00
notion_page_id: 2f512b31-a8a8-80aa-9d7d-e7005568e96f
layout: post
categories:
  - Data Engineering
tags:
  - "DE"
  - "POSTGRESQL"
  - "DB"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

> **시리즈 소개**: 프로덕션 환경에서 PostgreSQL 데이터베이스 성능을 최적화한 실전 사례를 5개 파트로 나눠 공유합니다.
- **Part 1: 문제 정의와 성능 분석**

- Part 2: 최적화 전략 수립

- Part 3: Dashboard 쿼리 최적화 (21배 개선)

- Part 4: 검색과 JOIN 최적화 (22배, 19배 개선)

- Part 5: 모니터링과 결과

---

## **1. 서론: 왜 데이터베이스 최적화가 필요했는가**

### **Referread 서비스 소개**

[Referread](https://www.referread.ai/) 는 AI 기반 콘텐츠 리서치 플랫폼입니다. 사용자는 브랜드와 토픽을 입력하면, AI가 SEO 최적화된 콘텐츠 아이디어와 키워드를 자동으로 생성해줍니다.

**기술 스택:**

- Frontend: React + TypeScript + Vite

- Backend: Supabase (PostgreSQL + Edge Functions)

- Workflow: n8n

- Deployment: Google Cloud Storage + CDN

### **문제 상황**

서비스를 운영하면서 다음과 같은 문제들이 발생했습니다:

1. **Dashboard 로딩 지연**
  - 프로젝트가 100개 이상일 때 3초 이상 소요

  - 사용자가 "느리다"는 피드백 증가

2. **Admin 검색 응답 지연**
  - 검색어를 입력할 때마다 0.5초 이상 대기

  - 타이핑할 때마다 버벅임

3. **SavedTopics 페이지 무한 로딩**
  - 데이터가 많을 때 로딩이 끝나지 않음

  - 네트워크 탭에서 250KB 이상의 JSON 응답 확인

### **최적화 목표**

- **사용자 경험 개선**: 모든 페이지 로딩 1초 이내

- **서버 리소스 절약**: Database CPU 사용률 20% 

- **확장성 확보**: 프로젝트 1,000개 이상에서도 빠른 응답

---

## **2. 데이터베이스 구조 분석**

### **도메인 모델**

```plain text
Brand (브랜드)
   └── Project (리서치 프로젝트)
        ├── Topic (생성된 콘텐츠 주제)
        ├── Related Keywords (연관 키워드)
        ├── Expanded Outlines (상세 아웃라인)
        └── Fan Out Logs (분석 로그)
```

### **주요 테이블 스키마**

**projects 테이블**:

```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,        -- 사용자 ID
  tenant_id UUID,                -- 조직 ID
  brand TEXT,                    -- 브랜드명
  topic TEXT,                    -- 주제
  hide BOOLEAN,                  -- 숨김 여부
  is_dev BOOLEAN,                -- 개발 환경 플래그
  status TEXT,                   -- 상태
  created_at TIMESTAMPTZ,        -- 생성 시간
  updated_at TIMESTAMPTZ         -- 수정 시간
);
```

**topics 테이블**:

```sql
CREATE TABLE topics (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL,      -- 프로젝트 FK
  main_keyword TEXT,             -- 메인 키워드
  is_selected BOOLEAN,           -- 저장 여부
  is_deleted BOOLEAN,            -- 소프트 삭제
  created_at TIMESTAMPTZ         -- 생성 시간
);
```

**related_keywords 테이블**:

```sql
CREATE TABLE related_keywords (
  id UUID PRIMARY KEY,
  project_id UUID NOT NULL,      -- 프로젝트 FK
  keyword TEXT,                  -- 키워드
  google_msv INTEGER             -- Google 월간 검색량
);
```

### **페이지별 쿼리 패턴 분석**

### **Dashboard (높은 접근 빈도)**

**프로젝트 리스트 조회:**

```sql
SELECT * FROM projects
WHERE user_id = 'user-123'
  AND (hide IS NULL OR hide = false)
  AND is_dev = false
ORDER BY created_at DESC;
```

**브랜드 리스트 조회:**

```sql
SELECT * FROM brands
WHERE user_id = 'user-123'
  AND is_dev = false
ORDER BY updated_at DESC;
```

### **AdminDashboard (검색 + 페이지네이션)**

**검색 쿼리**:

```sql
SELECT * FROM projects
WHERE is_dev = false
  AND (topic ILIKE '%AI%' OR brand ILIKE '%AI%')  -- ⚠️ 성능 문제!
ORDER BY created_at DESC
LIMIT 50 OFFSET 0;
```

**문제점:**

- `ILIKE '%keyword%'` 패턴은 인덱스를 활용할 수 없음

- 항상 전체 테이블 스캔 (Seq Scan)

- 프로젝트 5,000개일 때 500ms 이상 소요

### **ResearchResults (JOIN 빈번)**

**토픽 조회**:

```sql
SELECT t.*, p.region
FROM topics t
JOIN projects p ON t.project_id = p.id
WHERE t.project_id = 'project-abc'
  AND (t.is_deleted IS NULL OR t.is_deleted = false)
ORDER BY t.created_at ASC;
```

**관련 키워드 조회:**

```sql
SELECT * FROM related_keywords
WHERE project_id = 'project-abc'
ORDER BY google_msv DESC NULLS LAST;
```

### **SavedTopics**

**저장된 토픽 조회**:

```sql
SELECT t.*, p.brand, p.region, p.user_id, p.hide
FROM topics t
JOIN projects p ON t.project_id = p.id
WHERE t.is_selected = true
  AND p.user_id = 'user-123';
```

**문제점** (line 113-115):

```typescript
// ⚠️ 클라이언트 사이드 필터링!
const filteredData = (data || []).filter(
  (t) => !(t.projects as Record<string, unknown>)?.hide
);
```

- 서버에서 `hide = true`인 데이터까지 모두 가져옴

- 클라이언트에서 필터링 → 불필요한 네트워크 데이터 전송

- 1,000개 중 700개를 버리는 상황 발생

---

## **3. 성능 병목 지점 찾기: EXPLAIN ANALYZE 활용법**

### **EXPLAIN ANALYZE란?**

PostgreSQL에서 제공하는 쿼리 실행 계획 분석 도구입니다. 쿼리가 어떻게 실행되는지, 어디서 시간이 오래 걸리는지 정확히 알려줍니다.

**기본 사용법:**

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM projects
WHERE user_id = 'user-123'
ORDER BY created_at DESC;

```

**옵션 설명:**

- `ANALYZE`: 실제로 쿼리를 실행하고 결과 측정

- `BUFFERS`: 메모리/디스크 I/O 정보 표시

- `VERBOSE`: 컬럼 정보 등 상세 출력

### **EXPLAIN 결과 해석하기**

### **예시 1: Seq Scan (나쁨)**

```sql
Seq Scan on projects  (cost=0.00..150.00 rows=5000 width=200)
                       (actual time=0.123..345.678 rows=50 loops=1)
  Filter: (user_id = 'user-123' AND (hide IS NULL OR hide = false))
  Rows Removed by Filter: 4850
Planning Time: 0.5 ms
Execution Time: 387.2 m
```

**문제점:**

- `Seq Scan`: 테이블 전체를 처음부터 끝까지 읽음

- `Rows Removed by Filter: 4850`: 5,000개 중 4,850개를 읽었다가 버림

- `Execution Time: 387.2 ms`: 사용자 체감 지연

### **예시 2: Index Scan (좋음)**

```sql
Index Scan using idx_projects_user_hide_dev_created on projects
  (cost=0.15..8.50 rows=50 width=200)
  (actual time=0.012..15.234 rows=50 loops=1)
  Index Cond: (user_id = 'user-123' AND is_dev = false)
  Filter: (hide IS NULL OR hide = false)
  Rows Removed by Filter: 0
Planning Time: 0.3 ms
Execution Time: 18.1 ms
```

**개선 효과:**

- `Index Scan`: 인덱스를 사용해 필요한 행만 직접 접근

- `Rows Removed by Filter: 0`: 불필요한 행을 읽지 않음

- `Execution Time: 18.1 ms`: **387ms → 18ms (21배 개선)**

### **주요 지표 해석**

### **실전 분석: Dashboard 쿼리**

**최적화 전:**

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM projects
WHERE user_id = '018d1234-5678-9abc-def0-123456789abc'
  AND (hide IS NULL OR hide = false)
  AND is_dev = false
ORDER BY created_at DESC;
```

**결과:**

```plain text
Gather Merge  (cost=5000.00..6000.00 rows=50 width=200)
              (actual time=345.123..387.456 rows=50 loops=1)
  Workers Planned: 2
  Workers Launched: 2
  ->  Sort  (cost=4000.00..4100.00 rows=25 width=200)
            (actual time=340.567..340.789 rows=17 loops=3)
        Sort Key: created_at DESC
        Sort Method: quicksort  Memory: 25kB
        Worker 0:  Sort Method: quicksort  Memory: 25kB
        Worker 1:  Sort Method: quicksort  Memory: 25kB
        ->  Parallel Seq Scan on projects
            (cost=0.00..3500.00 rows=25 width=200)
            (actual time=0.123..335.678 rows=17 loops=3)
              Filter: (user_id = '018d1234-...' AND
                       (hide IS NULL OR hide = false) AND
                       is_dev = false)
              Rows Removed by Filter: 1617
Buffers: shared hit=2000 read=500
Planning Time: 1.234 ms
Execution Time: 387.891 ms
```

**핵심 문제:**

1. `Parallel Seq Scan`: 병렬로 전체 테이블을 읽음

2. `Rows Removed by Filter: 1617 × 3 workers = 4,851`: 대부분의 행을 버림

3. `Execution Time: 387.891 ms`: 사용자 체감 지연

**왜 인덱스를 사용하지 않았을까?**

- 인덱스가 아예 없음 (아직 생성 전)

- PostgreSQL은 인덱스가 없으면 무조건 Seq Scan

---

## **4. 다음 단계: 최적화 전략 수립**

이제 문제를 정확히 파악했으니, Part 2에서는 구체적인 최적화 전략을 수립합니다:

1. **ANALYZE로 통계 정보 업데이트**
  - 쿼리 플래너가 정확한 판단을 내리도록 돕기

2. **전략적 인덱스 설계**
  - 어떤 컬럼에 인덱스를 만들 것인가?

  - 복합 인덱스 vs 단일 인덱스

  - Partial Index로 인덱스 크기 80% 절감

3. **쿼리 리팩토링**
  - 클라이언트 필터링 → 서버 필터링

  - ILIKE → Full Text Search

---