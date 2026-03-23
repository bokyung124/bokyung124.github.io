---
title: "Leetcode) 3764. Most Common Course Pairs"
last_modified_at: 2026-03-23T18:39:00+00:00
notion_page_id: 32c12b31-a8a8-8073-9fdf-da39c18a2bd0
layout: post
categories:
  - Algorithm
tags:
  - "LeetCode"
  - "Algorithm"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

### 문제

[https://leetcode.com/problems/most-common-course-pairs/description/](https://leetcode.com/problems/most-common-course-pairs/description/)

```
+-------------------+---------+
| Column Name       | Type    |
+-------------------+---------+
| user_id           | int     |
| course_id         | int     |
| course_name       | varchar |
| completion_date   | date    |
| course_rating     | int     |
+-------------------+---------+
(user_id, course_id) is the combination of columns with unique values for this table.
Each row represents a completed course by a user with their rating (1-5 scale).
```

Write a solution to identify **skill mastery pathways** by analyzing course completion sequences among top-performing students:

- Consider only **top-performing students** (those who completed **at least **`5`** courses** with an **average rating of **`4`** or higher**).

- For each top performer, identify the **sequence of courses** they completed in chronological order.

- Find all **consecutive course pairs** (`Course A → Course B`) taken by these students.

- Return the **pair frequency**, identifying which course transitions are most common among high achievers.

Return *the result table ordered by* *pair frequency in ****descending**** order* *and then by first course name and second course name in ****ascending**** order*.


### 풀이 1 - 우수 학생 먼저 필터링

```sql
WITH TopStudents AS (
    SELECT user_id
    FROM course_completions
    GROUP BY user_id
    HAVING COUNT(course_id) >= 5 
    AND AVG(course_rating) >= 4.0
), 

CourseFair AS (
    SELECT
        c.user_id,
        course_name AS first_course,
        LEAD(c.course_name) OVER(
            PARTITION BY c.user_id
            ORDER BY completion_date
        ) AS second_course
    FROM course_completions c
    INNER JOIN TopStudents t ON c.user_id = t.user_id 
)

SELECT 
    first_course,
    second_course,
    COUNT(*) AS transition_count
FROM CourseFair
WHERE second_course IS NOT NULL
GROUP BY 
    first_course, 
    second_course
ORDER BY 
    transition_count DESC,
    first_course ASC,
    second_course ASC
```

### 풀이 2 - 한 번에 쿼리

```sql
WITH CoursePair AS (
    SELECT
        course_name AS first_course,
        LEAD (course_name) OVER (
            PARTITION BY user_id
            ORDER BY completion_date
        ) AS second_course,

        COUNT(*) OVER( PARTITION BY user_id ) AS total_courses,
        AVG(course_rating) OVER ( PARTITION BY user_id ) AS avg_rating
    FROM course_completions
)

SELECT
    first_course,
    second_course,
    COUNT(*) AS transition_count
FROM CoursePair
WHERE total_courses >= 5
    AND avg_rating >= 4.0
    AND second_course IS NOT NULL
GROUP BY first_course, second_course
ORDER BY transition_count DESC, first_course, second_course
```


### 리뷰

- 풀이 1 vs. 풀이 2
  - `풀이 1`: 우수 학생 목록을 먼저 CTE로 필터링한 뒤, 그 안에서 수강 기록 집계

  - `풀이 2`: 모든 데이터에 대해 수강 기록을 먼저 집계한 뒤, 최종 쿼리에서 우수 학생 필터링

  - 데이터가 수천만 건 이상으로 많아질 경우 선 필터링 방식 (`풀이 1`) 이 더 유리함

- **강의 쌍** 을 찾아야 하기 때문에 가장 마지막 (`second_course IS NULL` )인 행은 제외해야 함


### 윈도우 함수

- `LEAD()`
  - 현재 행 기준으로 다음 행 (또는 N번째 행)의 특정 컬럼을 가져오는 윈도우 함수
    - 이전 행을 가져오는 함수는 `LAG()`

- `PARTITION BY`
  - 그룹화! 데이터를 특정 기준에 따라 나눔. 

  - 위 문제에서는 연속된 강의를 **학생 별로** 집계해야 하기 때문에 `PARTITION BY` 를 이용하여 `user_id` 로 그룹을 나눔

  - `ORDER BY` 를 이용하여 그룹 안에서 행의 순서를 정렬함
    - → 각 학생 별로 `completion_date` 기준으로 강의를 정렬함 → 현재 행의 `course_name` 이 `first_course`, 다음 행의 `course_name`이 `second_course` 가 됨.

- `AVG(course_rating) OVER(PARTITION BY user_id)`
  - 마찬가지로 `user_id` 기준으로 그룹화하여 각 그룹에서의 `course_rating`의 평균을 모든 행에 추가함 
    - → 추후 이 값으로 user를 필터링하기 위해 사용.

### GROUP BY 대신 PARTITION BY 를 사용하는 사례 

- `PARTITION BY` 를 사용하면 **원본 데이터의 개별 행이 유지**된다는 것이 가장 큰 차이

- **개별 값과 그룹의 통계값을 비교해야 할 때**
  - e.g.
    - 이 사람의 연봉은 속한 부서의 평균 연봉보다 얼마나 높을까?
    - 이 금액은 해당 고객이 평생 사용한 총액의 몇 %를 차지할까?
  - `GROUP BY`를 사용하면 평균값, 총액 등은 구할 수 있지만, 상세 데이터는 사라지기 때문에 두 값을 비교하려면 원본 테이블과 JOIN하는 과정이 추가되어야 함

- **그룹 별로 순위를 매겨야 할 때 (Top N 추출)**
  - e.g.
    - 각 부서 별로 연봉이 가장 높은 상위 3명의 직원 이름과 직급 추출

- **누적합이나 이동 평균을 구할 때**
  - e.g.
    - 한 고객이 1월에 만원, 2월에 2만원, 3월에 3만원을 사용했을 때, 각 달 별로 그 달까지의 누적 결재액을 구하는 경우
  - `GROUP BY`는 전체 기간을 합친 값만 보여줄 수 있음

- **이전/다음 데이터와 비교할 때 (흐름 분석)**
  - e.g.
    - 고객이 이전 결제일로부터 며칠 만에 재구매했는지