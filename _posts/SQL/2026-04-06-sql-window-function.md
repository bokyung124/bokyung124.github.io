---
title: "[SQL] Window Function"
last_modified_at: 2026-04-06T15:09:00+00:00
notion_page_id: 33a12b31-a8a8-80d7-8f0a-c302a45bce14
layout: post
categories:
  - SQL
tags:
  - "Data Engineering"
  - "SQL"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

## Window Function

- 행과 행 간의 관계를 쉽게 정의하기 위해 만들어진 함수

- `GROUP BY` 와의 비교
  - `GROUP BY (집계 함수)`: 여러 행을 그룹화하여 **하나의 행으로 압축** → 개별 행의 디테일이 사라짐

  - `Window Function`: 행들을 그룹화하지만, **원래의 행을 그대로 유지**하면서, 각 행 옆에 계산된 결과값을 추가함
    - 계산되는 범위를 **윈도우**라고 함

### 기본 문법 구조

```sql
SELECT 
    [윈도우 함수명](컬럼명) OVER (
        PARTITION BY [그룹화할 컬럼] 
        ORDER BY [정렬할 컬럼] 
        ROWS or RANGE [프레임 범위]
    )
FROM 테이블명;
```

- `**OVER()**` : 이 함수가 윈도우 함수임을 선언하는 필수 키워드

- `**PARTITION BY**`: 어떤 단위로 윈도우(그룹)를 나눌지 결정
  - 생략 시 전체 데이터가 하나의 윈도우가 됨

- `**ORDER BY**`: 윈도우 내에서 행들을 어떤 순서로 정렬할지 결정
  - 누적합 / 순위를 구할 때 필수적

- `**ROWS / RANGE**`: 윈도우 내에서 연산할 행의 범위를 더 디테일하게 지정
  - e.g. 현재 행 기준 앞의 2개 행부터 뒤의 1개 행까지

## 윈도우 함수 종류

### 순위 함수

- `**ROW_NUMBER()**`: 중복 없는 고유한 순위 부여 (1, 2, 3, 4)

- `**RANK()**`: 동점 시 같은 순위 부여, 다음 순위는 건너뜀 (1, 2, 2, 4)

- `**DENSE_RANK()**`: 동점 시 같은 순위 부여, 다음 순위 안 건너뜀 (1, 2, 2, 3)

예시: **부서별로 급여가 높은 순서대로 순위를 매겨보자.**

```sql
SELECT
	name,
	department,
	salary,
	RANK() OVER (PARTITION BY deparment ORDER BY salary DESC) AS salary_rank
FROM employees;
```

- 부서 별로 윈도우가 나뉘고, 그 안에서 급여 내림차순으로 순위가 매겨짐

### 집계 함수

- `**SUM**`**, **`**AVG**`**, **`**MAX**`**, **`**MIN**`**, **`**COUNT**`

예시: ** 직원의 급여 데이터 옆에 '부서 평균 급여'와 '전체 누적 급여합'을 같이 보고 싶다**

```sql
SELECT
	name,
	department,
	salary,
	AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,
	SUM(salary) OVER (ORDER BY emp_id) AS cumulative_salary
FROM employees;
```

- `AVG`에 `PARTITION BY`만 쓰면 해당 부서의 평균 급여가 모든 행에 채워짐

- `SUM`에 `ORDER BY`를 쓰면 사번 순서대로 **누적 합계**가 계산됨

### 순서 함수

- `**LAG(컬럼, 칸 수)**`: 현재 행 기준 **이전 행**의 값을 가져옴

- `**LEAD(컬럼, 칸 수)**`: 현재 행 기준 **다음 행**의 값을 가져옴

예시: **내 급여와 '내 바로 앞 사번 직원의 급여'를 비교해보자.**

```sql
SELECT
	emp_id,
	name,
	salary,
	LAG(salary, 1) OVER (ORDER BY emp_id) AS prev_emp_salary,
	salary - LAG(salary, 1) OVER (ORDER BY emp_id) AS diff_salary
FROM employees;
```

## 주의할 점

### 윈도우 함수로 구한 결과로 WHERE 절에서 필터링할 수 없음

- SELECT 단계이기 때문에 WHERE, GROUP BY 보다 나중에 실행됨

- 윈도우 함수 결과를 조건절에 쓰려면 **서브쿼리**나 **CTE**를 사용해야 함

```sql
WITH RankedEmployees AS (
    SELECT 
        name, 
        department, 
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rnk
    FROM Employees
)
SELECT name, department, salary
FROM RankedEmployees
WHERE rnk = 1;
```

- 성능 주의
  - 특히 `PARTITION BY` 와 `ORDER BY` 를 대용량 데이터에 사용할 경우, 내부적으로 정렬 작업이 발생하므로 쿼리 비용이 높아질 수 있음

  - 적절한 인덱스를 태우거나, 범위를 제한하는 것이 좋음

### 집계 함수에서 ORDER BY 사용 주의

- SUM, COUNT, AVG 등 집계 함수는 `ORDER BY` 유무에 따라 함수의 성격이 완전히 바뀜

- **ORDER BY가 없을 때** → **전체 집계**
  - `SUM(salary) OVER (PARTITION BY department)`

  - 해당 부서 사람들의 총 급여

- **ORDER BY가 있을 때** → **누적 집계**
  - `SUM(salary) OVER (PARTITION BY department ORDER BY emp_id)`

  - emp_id 순서대로 **현재 행까지의 누적 salary 합** 을 구함

- <비교> 순위 함수 & 탐색 함수는 반드시 `ORDER BY` 가 필요한 함수들임

## Window Frame

- 윈도우 함수는 파티션 내에서 **어디서부터 어디까지를 계산할지 범위 (Frame)** 를 지정할 수 있음

- 명시적으로 적지 않아도 SQL 내부적으로 기본값이 존재 ⇒ 이 값이 `ORDER BY`에 따라 달라짐

- Frame의 범위를 지정할 때 사용하는 키워드 → `BETWEEN [시작] AND [끝]` 형태로 범위 생성
  - **UNBOUNDED PRECEDING**: 그룹의 맨 처음

  - **[N] PRECEDING**: 현재 행 기준 N개 앞의 행

  - **CURRENT ROW**: 현재 행

  - **[N] FOLLOWING**: 현재 행 기준 N개 뒤의 행

  - **UNBOUNDED FOLLOWING**: 그룹의 맨 끝

- e.g. `BETWEEN 1 PRECEDING AND 1 FOLLOWING`: 내 앞의 1행 ~ 내 뒤 1행 → 총 3개 행 계산!

## Range vs. ROW: 프레임의 범위를 잡는 기준

- **ROWS**
  - 물리적 기준 - **행** 단위로 계산함

  - `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
    - 무조건 내 윗 줄까지의 데이터와 현재 내 줄의 데이터만 더함

- **RANGE**
  - 논리적 값 기준 - `ORDER BY`에 쓰인 **값** 을 기준으로 계산함

  - `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
    - 만약 나랑 `ORDER BY` 값이 같은 행이 있으면, 그 행들까지 한 번에 묶어서 계산

**예시: 급여 순으로 누적합을 구하는 경우 (100, 200, 200, 300)**

- `SUM(salary) OVER(ORDER BY salary ``**ROWS**`` ...)`
  - 1번째 사람(100): 100

  - 2번째 사람(200): 100 + 200 = 300

  - 3번째 사람(200): 100 + 200 + 200 = 500
    - *순수하게 행 단위로 더함*

- `SUM(salary) OVER(ORDER BY salary ``**RANGE**`` ...)` **(SQL 기본 동작)**
  - 1번째 사람(100): 100

  - 2번째 사람(200): 100 + **(200+200)** = 500
    - *200이 두 명이니 같은 그룹으로 묶어서 한 번에 더해버림*

  - 3번째 사람(200): 100 + **(200+200)** = 500

- 가이드
  - 윈도우 함수에서 누적합을 구할 때, 프레임을 명시하지 않으면 **RANGE가 기본으로 작동**

  - 동점자(같은 날짜, 같은 급여 등)가 있을 때 묶어서 계산해야 한다면 → 프레임 생략 또는 RANGE 사용

  - 동점자가 있더라도 철저하게 위에서부터 한 줄씩 누적 계산을 해야 한다면 → 반드시 `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` 를 명시할 것!