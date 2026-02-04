---
title: "**PostgreSQL 쿼리 성능 20배 개선하기 (Part 2) - 최적화 전략 수립**"
last_modified_at: 2026-02-04T05:37:00+00:00
notion_page_id: 2fd12b31-a8a8-8098-bb5b-e87ee9d75a39
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

- **Part 2: 최적화 전략 수립**

- Part 3: Dashboard 쿼리 최적화 (21배 개선)

- Part 4: 검색과 JOIN 최적화 (22배, 19배 개선)

- Part 5: 모니터링과 결과

---

## **1. 최적화 전략 개요**

Part 1에서 EXPLAIN ANALYZE로 문제를 정확히 파악했습니다. 이제 세 가지 전략으로 최적화를 진행합니다:

1. **ANALYZE**: 통계 정보 업데이트로 쿼리 플래너의 정확한 판단 유도

2. **INDEX**: 전략적 인덱스 설계로 Seq Scan → Index Scan 전환

3. **Query Refactoring**: 비효율적인 쿼리 패턴 개선

---

## **2. 최적화 전략 1: ANALYZE로 통계 정보 업데이트**

### **ANALYZE가 필요한 이유**

PostgreSQL의 쿼리 플래너는 **통계 정보**를 바탕으로 최적의 실행 계획을 수립합니다. 하지만 이 통계가 오래되면 잘못된 판단을 내립니다.

**예시: 잘못된 카디널리티 추정**

```sql
-- 쿼리 플래너의 예상 (통계 오래됨)
Seq Scan on projects  (cost=0.00..150.00 rows=5000 width=200)
                      ^^^^ 5,000개 예상

-- 실제 결과
Seq Scan on projects  (actual time=0.123..345.678 rows=50 loops=1)
                                                     ^^^ 실제는 50개
```

플래너가 5,000개를 읽을 것으로 예상했지만, 실제로는 50개만 필요했습니다. 이런 오판이 쌓이면 비효율적인 실행 계획이 선택됩니다.

### **ANALYZE 실행 방법**

**수동 실행** (Supabase SQL Editor):

```sql
-- 특정 테이블
ANALYZE projects;
ANALYZE topics;
ANALYZE related_keywords;

-- 전체 데이터베이스
ANALYZE;
```

**언제 실행해야 하나?**

- 인덱스 생성 직후 (필수)

- 대량 데이터 INSERT/DELETE 후

- 쿼리 성능이 갑자기 나빠졌을 때

- 월 1회 정기 실행 (권장)

### **autovacuum 설정 조정**

PostgreSQL은 `autovacuum` 프로세스가 자동으로 ANALYZE를 실행합니다. 하지만 기본 설정은 너무 보수적입니다.

**기본 설정:**

- 테이블 행의 **10%가 변경**되면 ANALYZE 실행

- 5,000개 테이블이면 500개 변경 후에야 실행

**개선된 설정:**

```sql
-- Projects 테이블: 10% → 5%로 변경 (2배 더 자주)
ALTER TABLE projects SET (autovacuum_analyze_scale_factor = 0.05);
ALTER TABLE projects SET (autovacuum_analyze_threshold = 50);

-- Topics 테이블
ALTER TABLE topics SET (autovacuum_analyze_scale_factor = 0.05);
ALTER TABLE topics SET (autovacuum_analyze_threshold = 50);
```

**효과:**

- 통계 정보가 항상 최신 상태 유지

- 쿼리 플래너의 정확한 카디널리티 추정

- 빠르게 증가하는 테이블에 특히 유용

### **통계 정밀도 증가**

검색에 자주 사용되는 컬럼은 통계 샘플 수를 늘립니다.

```sql
-- 기본값: 100 샘플 → 200 샘플로 증가
ALTER TABLE projects ALTER COLUMN topic SET STATISTICS 200;
ALTER TABLE projects ALTER COLUMN brand SET STATISTICS 200;

-- Topics 테이블
ALTER TABLE topics ALTER COLUMN main_keyword SET STATISTICS 200;

-- Related Keywords 테이블
ALTER TABLE related_keywords ALTER COLUMN keyword SET STATISTICS 200;
ALTER TABLE related_keywords ALTER COLUMN google_msv SET STATISTICS 200;
```

**효과:**

- 더 정확한 통계 정보 수집

- Full Text Search 쿼리 최적화

- 다양한 검색 키워드에 대응

---

## **3. 최적화 전략 2: 전략적 인덱스 설계**

### **인덱스란?**

책의 **색인**과 같은 개념입니다. 책 전체를 처음부터 읽지 않고, 색인에서 페이지 번호를 찾아 바로 이동하듯이, 인덱스를 사용하면 테이블 전체를 읽지 않고 필요한 행만 빠르게 찾을 수 있습니다.

### **안티패턴: 각 컬럼마다 단일 인덱스**

**잘못된 접근:**

```sql
-- ❌ 나쁜 예시
CREATE INDEX idx_projects_user_id ON projects (user_id);
CREATE INDEX idx_projects_is_dev ON projects (is_dev);
CREATE INDEX idx_projects_created_at ON projects (created_at);
```

**문제점:**

```sql
-- 이 쿼리는 위 인덱스 중 하나만 사용 가능
SELECT * FROM projects
WHERE user_id = 'user-123'
  AND is_dev = false
ORDER BY created_at DESC;

-- PostgreSQL은 user_id 인덱스만 사용하고
-- is_dev는 여전히 필터링으로 처리
Index Scan using idx_projects_user_id  (cost=...)
  Index Cond: (user_id = 'user-123')
  Filter: (is_dev = false)  -- ⚠️ 인덱스 활용 못함
  Rows Removed by Filter: 2500
```

### **베스트 프랙티스: 복합 인덱스 (Composite Index)**

**올바른 접근:**

```sql
-- ✅ 좋은 예시: 복합 인덱스
CREATE INDEX idx_projects_user_hide_dev_created
ON projects (user_id, is_dev, created_at DESC)
WHERE (hide IS NULL OR hide = false);
```

**장점:**

```sql
-- 모든 조건을 인덱스로 처리
Index Scan using idx_projects_user_hide_dev_created  (cost=...)
  Index Cond: (user_id = 'user-123' AND is_dev = false)
  Filter: None
  Rows Removed by Filter: 0  -- ✅ 완벽!
```

### **복합 인덱스 컬럼 순서의 중요성**

**컬럼 순서 규칙:**

1. **WHERE 절 등호 조건** (가장 선택적인 컬럼 우선)

2. **ORDER BY / GROUP BY 컬럼**

3. **범위 조건** (>, <, BETWEEN)

**예시:**

```sql
-- ✅ 올바른 순서
CREATE INDEX idx_projects_user_hide_dev_created
ON projects (
  user_id,         -- 1. WHERE user_id = ? (선택도 높음, 1%)
  is_dev,          -- 2. WHERE is_dev = ? (환경 분리)
  created_at DESC  -- 3. ORDER BY created_at DESC
);

-- ❌ 잘못된 순서
CREATE INDEX idx_projects_created_user
ON projects (
  created_at DESC,  -- ORDER BY를 먼저 두면
  user_id           -- WHERE 조건이 비효율적
);
```

**왜 잘못됐을까?**

- `created_at`이 먼저 오면, 전체 시간순으로 정렬된 인덱스

- `user_id` 필터링이 인덱스의 일부만 사용 가능

- 결국 많은 행을 읽은 후 필터링

### **Partial Index (부분 인덱스): 인덱스 크기 80% 절감**

**개념:**

```sql
-- ✅ WHERE 절로 인덱싱 대상 제한
CREATE INDEX idx_projects_user_hide_dev_created
ON projects (user_id, is_dev, created_at DESC)
WHERE (hide IS NULL OR hide = false);
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- 조건을 만족하는 행만 인덱싱
```

**효과:**

- `hide = true`인 프로젝트는 인덱스에 포함되지 않음

- 인덱스 크기: 500MB → 100MB (80% 절감)

- 더 작은 인덱스 = 더 빠른 검색

- 메모리 캐시에 더 많이 적재

**주의사항:** 쿼리의 WHERE 절이 인덱스의 WHERE 절과 일치해야 사용됩니다.

```sql
-- ✅ 인덱스 사용 O
SELECT * FROM projects
WHERE user_id = 'user-123'
  AND (hide IS NULL OR hide = false);  -- 인덱스 조건과 일치

-- ❌ 인덱스 사용 X
SELECT * FROM projects
WHERE user_id = 'user-123';  -- hide 조건 누락
```

### **GIN Index: Full Text Search 필수**

ILIKE 검색은 인덱스를 활용할 수 없습니다.

**문제 있는 쿼리:**

```sql
-- ❌ 항상 Seq Scan
SELECT * FROM projects
WHERE topic ILIKE '%AI%' OR brand ILIKE '%AI%';

Seq Scan on projects  (cost=0.00..5000.00 rows=50 width=200)
  Filter: (topic ~~* '%AI%' OR brand ~~* '%AI%')
  Rows Removed by Filter: 4950
Execution Time: 512.3 ms
```

**해결: GIN Index + to_tsvector**

```sql
-- ✅ GIN 인덱스 생성
CREATE INDEX idx_projects_search_fts
ON projects USING gin (
  to_tsvector('simple', coalesce(topic, '') || ' ' || coalesce(brand, ''))
)
WHERE (hide IS NULL OR hide = false);

-- 쿼리 변경
SELECT * FROM projects
WHERE to_tsvector('simple', coalesce(topic, '') || ' ' || coalesce(brand, ''))
      @@ to_tsquery('simple', 'AI:*');

Bitmap Index Scan on idx_projects_search_fts  (cost=...)
  Index Cond: (to_tsvector(...) @@ to_tsquery(...))
Execution Time: 23.1 ms  -- 512ms → 23ms (22배 개선)
```

**GIN vs B-tree:**

---

## **4. 최적화 전략 3: 쿼리 리팩토링**

인덱스만으로 해결되지 않는 문제는 쿼리를 개선합니다.

### **문제 1: 클라이언트 사이드 필터링**

**현재 코드** (`supabase/functions/topics/index.ts:113-115`):

```typescript
// ❌ 서버에서 1,000개 가져온 후 클라이언트에서 700개 버림
const { data } = await supabase
  .from('topics')
  .select('*, projects(brand, region, user_id, hide)')
  .eq('is_selected', true)
  .eq('projects.user_id', userId);

const filteredData = (data || []).filter(
  (t) => !(t.projects as Record<string, unknown>)?.hide
);
```

**문제점:**

- 네트워크 전송: 250KB (1,000개)

- 클라이언트 처리 시간: 150ms

- 실제 사용: 75KB (300개)

- **낭비: 175KB (70%)**

**개선:**

```typescript
// ✅ 서버에서 필터링
const { data } = await supabase
  .from('topics')
  .select('*, projects(brand, region)')
  .eq('is_selected', true)
  .eq('projects.user_id', userId)
  .or('hide.is.null,hide.eq.false', { foreignTable: 'projects' });
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ -- 서버 사이드 필터링

// 클라이언트 필터링 제거
// const filteredData = ...  // 불필요
```

**효과:**

- 네트워크 전송: 75KB (300개)

- 클라이언트 처리 시간: 0ms

- **70% 네트워크 데이터 절감**