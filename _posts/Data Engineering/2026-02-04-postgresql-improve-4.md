---
title: "**PostgreSQL 쿼리 성능 20배 개선하기 (Part 4) - 검색과 JOIN 최적화**"
last_modified_at: 2026-02-04T05:39:00+00:00
notion_page_id: 2fd12b31-a8a8-8006-adbd-fd2d126130d5
layout: post
categories:
  - Data Engineering
tags:
  - "Data Engineering"
  - "DE"
  - "ORM"
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
- Part 1: 문제 정의와 성능 분석

- Part 2: 최적화 전략 수립

- Part 3: Dashboard 쿼리 최적화 (21배 개선)

- **Part 4: 검색과 JOIN 최적화 (22배, 19배 개선)** 

- Part 5: 모니터링과 결과

---

## **1. AdminDashboard 검색 최적화 (22배 개선)**

### **문제: ILIKE 검색은 인덱스를 활용할 수 없다**

Admin Dashboard에는 검색 기능이 있습니다. 사용자가 검색어를 입력하면 프로젝트의 `topic`과 `brand` 컬럼에서 검색합니다.

**현재 구현** (`supabase/functions/admin/index.ts:155`):

```typescript
if (search && search.trim()) {
  query = query.or(`topic.ilike.%${search}%,brand.ilike.%${search}%`);
}
```

**실제 실행되는 SQL:**

```sql
SELECT * FROM projects
WHERE is_dev = false
  AND (topic ILIKE '%AI%' OR brand ILIKE '%AI%')
ORDER BY created_at DESC
LIMIT 50;
```

### **EXPLAIN ANALYZE: 최적화 전**

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM projects
WHERE is_dev = false
  AND (topic ILIKE '%AI%' OR brand ILIKE '%AI%')
ORDER BY created_at DESC
LIMIT 50;
```

**결과:**

```plain text
Limit  (cost=5234.56..5235.68 rows=50 width=215)
       (actual time=510.123..512.345 rows=50 loops=1)
  Buffers: shared hit=2100 read=650

  ->  Sort  (cost=5234.56..5247.89 rows=53 width=215)
            (actual time=510.120..510.234 rows=50 loops=1)
        Sort Key: created_at DESC
        Sort Method: top-N heapsort  Memory: 45kB
        Buffers: shared hit=2100 read=650

        ->  Seq Scan on public.projects
            (cost=0.00..5123.75 rows=53 width=215)
            (actual time=0.345..507.890 rows=53 loops=1)
              Filter: ((is_dev = false) AND
                       ((topic ~~* '%AI%'::text) OR (brand ~~* '%AI%'::text)))
              Rows Removed by Filter: 4947
              Buffers: shared hit=2100 read=650

Planning Time: 1.123 ms
Execution Time: 512.456 ms
```

**핵심 문제:**

- `Seq Scan`: 전체 테이블 스캔 (인덱스 활용 불가)

- `Rows Removed by Filter: 4947`: 5,000개 중 4,947개 버림

- `Execution Time: 512.456 ms`: 타이핑할 때마다 0.5초 지연

**왜 B-tree 인덱스를 사용할 수 없나?**

```sql
-- ❌ B-tree 인덱스는 ILIKE '%keyword%'를 지원하지 않음
CREATE INDEX idx_projects_topic ON projects (topic);

-- B-tree는 다음 패턴만 지원:
topic = 'AI'              -- 정확한 일치
topic LIKE 'AI%'          -- 접두사 일치
topic > 'A' AND topic < 'B'  -- 범위 검색

-- 지원하지 않는 패턴:
topic ILIKE '%AI%'        -- 중간 일치
topic ILIKE '%AI'         -- 접미사 일치
```

### **해결책: GIN Index + Full Text Search**

PostgreSQL의 Full Text Search 기능을 사용하면 ILIKE를 완전히 대체할 수 있습니다.

**핵심 개념:**

1. `to_tsvector()`: 텍스트를 검색 가능한 토큰으로 변환

2. `to_tsquery()`: 검색어를 쿼리로 변환

3. `@@` 연산자: Full Text Search 매칭

4. GIN Index: Full Text Search 전용 인덱스

### **GIN 인덱스 생성**

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_search_fts
ON projects USING gin (
  to_tsvector('simple', coalesce(topic, '') || ' ' || coalesce(brand, ''))
)
WHERE (hide IS NULL OR hide = false)
  AND (is_gsc_analysis IS NULL OR is_gsc_analysis = false);

COMMENT ON INDEX idx_projects_search_fts IS
  'Admin dashboard search - GIN full text search on topic + brand';
```

**설명:**

- `to_tsvector('simple', ...)`: 'simple' 설정은 언어 분석 없이 토큰화
  - 'simple': 대소문자 구분 없이 단어 단위로 분리

  - 'english', 'korean' 등: 형태소 분석 + 불용어 제거

- `coalesce(topic, '') || ' ' || coalesce(brand, '')`: topic + brand 결합

- `WHERE` 절: Partial Index로 불필요한 데이터 제외

### **쿼리 변경**

**TypeScript 코드 수정:**

```typescript
// ❌ Before: ILIKE
if (search && search.trim()) {
  query = query.or(`topic.ilike.%${search}%,brand.ilike.%${search}%`);
}

// ✅ After: Full Text Search
if (search && search.trim()) {
  const tsquery = search.trim()
    .split(/\s+/)
    .map(word => `${word}:*`)
    .join(' & ');

  query = query.textSearch(
    'fts_combined',
    tsquery,
    { config: 'simple' }
  );
}
```

**실제 SQL:**

```sql
SELECT * FROM projects
WHERE is_dev = false
  AND to_tsvector('simple', coalesce(topic, '') || ' ' || coalesce(brand, ''))
      @@ to_tsquery('simple', 'AI:*')
ORDER BY created_at DESC
LIMIT 50;
```

**to_tsquery 패턴:**

- `'AI:*'`: "AI"로 시작하는 모든 단어 (AI, AIops, etc.)

- `'AI & content'`: "AI"와 "content" 모두 포함

- `'AI | ML'`: "AI" 또는 "ML" 포함

- `'AI & !marketing'`: "AI"는 포함하되 "marketing"은 제외

### **EXPLAIN ANALYZE: 최적화 후**

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT * FROM projects
WHERE is_dev = false
  AND to_tsvector('simple', coalesce(topic, '') || ' ' || coalesce(brand, ''))
      @@ to_tsquery('simple', 'AI:*')
ORDER BY created_at DESC
LIMIT 50;
```

**결과:**

```plain text
Limit  (cost=123.45..124.56 rows=50 width=215)
       (actual time=20.123..23.045 rows=50 loops=1)
  Buffers: shared hit=15

  ->  Sort  (cost=123.45..124.01 rows=53 width=215)
            (actual time=20.120..20.234 rows=50 loops=1)
        Sort Key: created_at DESC
        Sort Method: quicksort  Memory: 45kB
        Buffers: shared hit=15

        ->  Bitmap Heap Scan on public.projects
            (cost=45.67..120.89 rows=53 width=215)
            (actual time=5.123..18.456 rows=53 loops=1)
              Recheck Cond: (to_tsvector('simple'::regconfig,
                             (COALESCE(topic, ''::text) || ' '::text ||
                              COALESCE(brand, ''::text)))
                             @@ to_tsquery('simple'::regconfig, 'AI:*'::text))
              Filter: (is_dev = false)
              Rows Removed by Filter: 0
              Heap Blocks: exact=12
              Buffers: shared hit=15

              ->  Bitmap Index Scan on idx_projects_search_fts
                  (cost=0.00..45.54 rows=53 width=0)
                  (actual time=5.012..5.012 rows=53 loops=1)
                    Index Cond: (to_tsvector(...) @@ to_tsquery(...))
                    Buffers: shared hit=3

Planning Time: 0.345 ms
Execution Time: 23.123 ms
```

**개선 효과:**

- `Seq Scan` → `Bitmap Index Scan on idx_projects_search_fts`

- `Rows Removed by Filter: 0`: 불필요한 행을 읽지 않음

- `Buffers: 2750` → `15` (183배 감소)

- `Execution Time: 512ms` → `23ms` (**22배 개선**)

### **검색 정확도 비교**

**ILIKE vs Full Text Search:**

**추천:**

- 단일 키워드 검색: Full Text Search

- 정확한 구문 검색: ILIKE (필요시 병행)

---

## **2. ResearchResults Topics 조회 최적화 (19배 개선)**

### **문제: JOIN 쿼리의 Seq Scan**

ResearchResults 페이지는 프로젝트의 모든 토픽을 표시합니다. 토픽 테이블과 프로젝트 테이블을 JOIN해서 `region` 정보를 가져옵니다.

**현재 쿼리** (`supabase/functions/topics/index.ts:147-152`):

```sql
SELECT t.*, p.region
FROM topics t
JOIN projects p ON t.project_id = p.id
WHERE t.project_id = 'project-abc'
  AND (t.is_deleted IS NULL OR t.is_deleted = false)
ORDER BY t.created_at ASC;
```

### **EXPLAIN ANALYZE: 최적화 전**

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT t.*, p.region
FROM topics t
JOIN projects p ON t.project_id = p.id
WHERE t.project_id = '018d1234-5678-9abc-def0-123456789abc'
  AND (t.is_deleted IS NULL OR t.is_deleted = false)
ORDER BY t.created_at ASC;
```

**결과:**

```plain text
Sort  (cost=1234.56..1245.78 rows=450 width=300)
      (actual time=154.123..156.234 rows=450 loops=1)
  Sort Key: t.created_at
  Sort Method: quicksort  Memory: 125kB
  Buffers: shared hit=850 read=120

  ->  Hash Join  (cost=123.45..1200.67 rows=450 width=300)
                 (actual time=45.123..150.456 rows=450 loops=1)
        Hash Cond: (t.project_id = p.id)
        Buffers: shared hit=850 read=120

        ->  Seq Scan on topics t
            (cost=0.00..1050.00 rows=450 width=280)
            (actual time=0.234..145.678 rows=450 loops=1)
              Filter: ((project_id = '018d1234-...'::uuid) AND
                       ((is_deleted IS NULL) OR (is_deleted = false)))
              Rows Removed by Filter: 49550
              Buffers: shared hit=800 read=120

        ->  Hash  (cost=123.00..123.00 rows=1 width=36)
                  (actual time=0.045..0.045 rows=1 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=50

              ->  Index Scan using projects_pkey on projects p
                  (cost=0.15..123.00 rows=1 width=36)
                  (actual time=0.012..0.023 rows=1 loops=1)
                    Index Cond: (id = '018d1234-...'::uuid)
                    Buffers: shared hit=50

Planning Time: 1.456 ms
Execution Time: 156.789 ms
```

**핵심 문제:**

1. `Seq Scan on topics`: 전체 테이블 스캔

2. `Rows Removed by Filter: 49550`: 50,000개 중 49,550개 버림

3. `Hash Join`: 비효율적인 JOIN 방식 (작은 결과셋에는 Nested Loop가 더 효율적)

4. `Execution Time: 156.789 ms`: 사용자 체감 지연

### **해결책: 복합 인덱스 생성**

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_topics_project_created
ON topics (project_id, created_at ASC)
WHERE (is_deleted IS NULL OR is_deleted = false);

COMMENT ON INDEX idx_topics_project_created IS
  'Research results topics list - project_id + created_at ASC with is_deleted exclusion';
```

**설계 포인트:**

- `project_id`: WHERE 절 필터링 (선택도 높음)

- `created_at ASC`: ORDER BY (오래된 순)

- Partial Index: `is_deleted = false` (소프트 삭제 제외)

### **EXPLAIN ANALYZE: 최적화 후**

```sql
ANALYZE topics;

EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT t.*, p.region
FROM topics t
JOIN projects p ON t.project_id = p.id
WHERE t.project_id = '018d1234-5678-9abc-def0-123456789abc'
  AND (t.is_deleted IS NULL OR t.is_deleted = false)
ORDER BY t.created_at ASC;
```

**결과:**

```plain text
Nested Loop  (cost=0.30..15.67 rows=450 width=300)
             (actual time=0.023..7.890 rows=450 loops=1)
  Buffers: shared hit=12

  ->  Index Scan using idx_topics_project_created on topics t
      (cost=0.15..12.34 rows=450 width=280)
      (actual time=0.012..3.456 rows=450 loops=1)
        Index Cond: (project_id = '018d1234-...'::uuid)
        Filter: ((is_deleted IS NULL) OR (is_deleted = false))
        Rows Removed by Filter: 0
        Buffers: shared hit=8

  ->  Index Scan using projects_pkey on projects p
      (cost=0.15..0.17 rows=1 width=36)
      (actual time=0.001..0.001 rows=1 loops=450)
        Index Cond: (id = t.project_id)
        Buffers: shared hit=4

Planning Time: 0.234 ms
Execution Time: 8.123 ms
```

**개선 효과:**

1. `Seq Scan` → `Index Scan using idx_topics_project_created`

2. `Hash Join` → `Nested Loop` (작은 결과셋에 최적)

3. `Rows Removed by Filter: 0`: 완벽한 인덱스 활용

4. `Buffers: 970` → `12` (80배 감소)

5. `Execution Time: 156ms` → `8ms` (**19배 개선**)

### **Hash Join vs Nested Loop**

**Hash Join:**

- 큰 테이블 JOIN에 유리

- 메모리에 해시 테이블 생성

- 결과셋이 많을 때 효율적

**Nested Loop:**

- 작은 결과셋에 유리

- 인덱스를 사용해 직접 조인

- 외부 테이블 행마다 내부 테이블 인덱스 스캔

**이 경우 Nested Loop가 더 나은 이유:**

- 외부 테이블 (topics): 450개 (적음)

- 내부 테이블 (projects): 인덱스로 1개만 찾으면 됨