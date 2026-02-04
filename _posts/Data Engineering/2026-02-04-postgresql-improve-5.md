---
title: "**PostgreSQL 쿼리 성능 20배 개선하기 (Part 5) - 모니터링과 결과**"
last_modified_at: 2026-02-04T05:42:00+00:00
notion_page_id: 2fd12b31-a8a8-80c1-b73a-ee6bfb1aecf1
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

- Part 4: 검색과 JOIN 최적화 (22배, 19배 개선)

- **Part 5: 모니터링과 결과**

---

## **1. 성능 모니터링 및 지속적 개선**

최적화를 한 번 하고 끝나는 게 아닙니다. 지속적으로 모니터링하고 개선해야 합니다.

### **pg_stat_statements: 느린 쿼리 모니터링**

**설치** (Supabase는 기본 설치됨):

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

**느린 쿼리 TOP 10 조회:**

```sql
SELECT
  substring(query, 1, 100) AS short_query,
  calls,
  round(mean_exec_time::numeric, 2) AS avg_ms,
  round(max_exec_time::numeric, 2) AS max_ms,
  round((100 * mean_exec_time * calls / sum(mean_exec_time * calls) OVER ())::numeric, 2) AS percentage
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
  AND query NOT LIKE '%pg_catalog%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**결과 예시:**

```plain text
short_query                                          | calls | avg_ms | max_ms | percentage
-----------------------------------------------------|-------|--------|--------|------------
SELECT * FROM projects WHERE user_id = $1 AND...    | 15234 | 18.12  | 123.45 | 12.34
SELECT * FROM topics WHERE project_id = $1 AND...   | 8567  | 8.23   | 45.67  | 5.67
SELECT * FROM related_keywords WHERE project_id = $ | 6234  | 12.45  | 78.90  | 4.23
```

**분석:**

- `calls`: 실행 횟수 (높을수록 최적화 효과 큼)

- `avg_ms`: 평균 실행 시간 (목표: < 50ms)

- `max_ms`: 최대 실행 시간 (이상치 확인)

- `percentage`: 전체 쿼리 시간 중 비율

**통계 초기화** (최적화 전/후 비교용):

```sql
SELECT pg_stat_statements_reset();
```

### **인덱스 사용률 체크**

**자주 사용되는 인덱스 TOP 10:**

```sql
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan AS scans,
  idx_tup_read AS tuples_read,
  idx_tup_fetch AS tuples_fetched,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY idx_scan DESC
LIMIT 10;
```

**결과 예시:**

```plain text
tablename  | indexname                            | scans  | tuples_read | index_size
-----------|--------------------------------------|--------|-------------|------------
projects   | idx_projects_user_hide_dev_created   | 125340 | 6267000     | 96 kB
topics     | idx_topics_project_created           | 78560  | 3534200     | 512 kB
projects   | idx_projects_search_fts              | 12340  | 617000      | 128 kB
```

**해석:**

- `scans > 1000`: 자주 사용되는 인덱스 (유지)

- `scans < 100`: 거의 사용되지 않는 인덱스 (삭제 고려)

**사용되지 않는 인덱스 찾기:**

```sql
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan AS scans,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```

**조치:**

```sql
-- 사용되지 않는 인덱스 삭제 (스토리지 절약)
DROP INDEX CONCURRENTLY idx_unused_index;
```

### **테이블 Bloat 체크**

**Bloat란?**

- UPDATE/DELETE로 인한 "죽은 행(dead tuples)" 누적

- 테이블 크기는 커지는데 실제 데이터는 적음

- 쿼리 성능 저하 원인

**Bloat 확인:**

```sql
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
  n_dead_tup,
  n_live_tup,
  round(100 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_tables
JOIN pg_stat_user_tables USING (schemaname, tablename)
WHERE schemaname = 'public'
ORDER BY dead_pct DESC NULLS LAST;
```

**결과 예시:**

```plain text
tablename          | total_size | n_dead_tup | n_live_tup | dead_pct
-------------------|------------|------------|------------|----------
topics             | 25 MB      | 1234       | 48766      | 2.46
projects           | 5 MB       | 89         | 4911       | 1.78
related_keywords   | 15 MB      | 456        | 99544      | 0.46
```

**조치:**

- `dead_pct < 20%`: 정상 (VACUUM 자동 실행됨)

- `dead_pct > 20%`: VACUUM 실행

- `dead_pct > 50%`: VACUUM FULL 고려 (주의: 테이블 락)

```sql
-- 일반 VACUUM (온라인)
VACUUM topics;

-- VACUUM FULL (오프라인 - 테이블 락)
VACUUM FULL topics;  -- 주의: 프로덕션에서는 점검 시간에만
```

---

## **2. 결과 요약**

### **쿼리 성능 개선**

### **페이지 로딩 성능**

### **서버 리소스 절감**

### **비용 절감**

**Supabase Pro 플랜 기준:**

- **Database CPU 시간 절감**: 73%

- **월 비용 절감**: $120 → $35 (**$85 절감, 71%**)

- **연간 비용 절감**: $1,440 → $420 (**$1,020 절감**)

**절감 계산:**

- CPU 사용률: 45% → 12% (73% 감소)

- CPU 시간 과금: $0.05/hour per vCPU

- 월간 절감: 0.73 × 730 hours × $0.05 × 2 vCPU = **$53**

- Connection Pool 최적화: **$20**

- 추가 확장 불필요: **$12**

---

## **3. 주요 교훈**

### **1. 측정 없이 최적화 없다**

**EXPLAIN ANALYZE는 필수**

- 감으로 인덱스를 만들지 말 것

- 반드시 EXPLAIN ANALYZE로 검증

- Before/After 비교를 명확히

**잘못된 접근:**

```sql
-- ❌ 그냥 만들어 보기
CREATE INDEX idx_projects_topic ON projects (topic);
```

**올바른 접근:**

```sql
-- ✅ EXPLAIN ANALYZE 먼저 실행
EXPLAIN ANALYZE SELECT * FROM projects WHERE topic = 'AI';

-- 결과 분석 후 인덱스 설계
CREATE INDEX idx_projects_topic_user
ON projects (topic, user_id)
WHERE hide = false;

-- 인덱스 생성 후 재검증
ANALYZE projects;
EXPLAIN ANALYZE SELECT * FROM projects WHERE topic = 'AI';
```

### **2. 복합 인덱스 > 단일 인덱스**

**잘못된 패턴:**

```sql
-- ❌ 단일 인덱스 3개
CREATE INDEX idx_projects_user ON projects (user_id);
CREATE INDEX idx_projects_dev ON projects (is_dev);
CREATE INDEX idx_projects_created ON projects (created_at);
```

- PostgreSQL은 하나만 사용

- 나머지는 필터링으로 처리

- 스토리지 낭비

**올바른 패턴:**

```sql
-- ✅ 복합 인덱스 1개
CREATE INDEX idx_projects_user_dev_created
ON projects (user_id, is_dev, created_at DESC);
```

- 모든 조건을 인덱스로 처리

- 스토리지 효율적

- 성능 최적

### **3. 클라이언트 필터링 지양**

**문제 있는 코드:**

```typescript
// ❌ 서버에서 1,000개 가져온 후 클라이언트에서 700개 버림
const { data } = await supabase.from('topics').select('*');
const filtered = data.filter(t => !t.hide);
```

**개선된 코드:**

```typescript
// ✅ 서버에서 300개만 가져오기
const { data } = await supabase
  .from('topics')
  .select('*')
  .or('hide.is.null,hide.eq.false')
```

**효과:**

- 네트워크 데이터 70% 감소

- 클라이언트 메모리 절약

- 렌더링 속도 향상

### **4. Full Text Search는 필수**

**ILIKE를 피하라:**

```sql
-- ❌ 항상 Seq Scan
WHERE topic ILIKE '%keyword%'

-- ✅ GIN Index 활용
WHERE to_tsvector('simple', topic) @@ to_tsquery('simple', 'keyword:*');
```

**Full Text Search 장점:**

- 20배 이상 빠름

- 더 정확한 검색