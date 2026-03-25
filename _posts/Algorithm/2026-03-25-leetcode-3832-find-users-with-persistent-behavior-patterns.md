---
title: "Leetcode) 3832. Find Users with Persistent Behavior Patterns"
last_modified_at: 2026-03-25T16:30:00+00:00
notion_page_id: 32e12b31-a8a8-80a7-bf76-d3ee67abdddb
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

[https://leetcode.com/problems/find-users-with-persistent-behavior-patterns/description/](https://leetcode.com/problems/find-users-with-persistent-behavior-patterns/description/)

```
+--------------+---------+
| Column Name  | Type    |
+--------------+---------+
| user_id      | int     |
| action_date  | date    |
| action       | varchar |
+--------------+---------+
(user_id, action_date, action) is the primary key (unique value) for this table.
Each row represents a user performing a specific action on a given date.
```

Write a solution to identify **behaviorally stable users** based on the following definition:

- A user is considered **behaviorally stable** if there exists a sequence of **at least **`5`** consecutive days** such that:
  - The user performed **exactly one action per day** during that period.

  - The **action is the same** on all those consecutive days.

- If a user has multiple qualifying sequences, only consider the sequence with the **maximum length**.

Return *the result table ordered by* `streak_length` *in ****descending**** order*,* then by *`user_id` *in ****ascending**** order*.

### 풀이1 - 1차 통과

```sql
WITH action_length AS (
    SELECT
        user_id,
        action_date,
        action,
        COUNT(*) OVER (
            PARTITION BY user_id, action
            ORDER BY action_date
        ) AS streak_length
    FROM activity
), persistent_user AS (
    SELECT
        user_id,
        action,
        MAX(streak_length)
    FROM action_length
    WHERE streak_length >= 5
    GROUP BY user_id, action
)

SELECT
    a.user_id,
    a.action,
    MAX(a.streak_length) AS streak_length,
    MIN(a.action_date) AS start_date,
    MAX(a.action_date) AS end_date
FROM action_length a
JOIN persistent_user p 
    ON a.user_id = p.user_id 
    AND a.action = p.action
GROUP BY user_id, action
ORDER BY streak_length DESC, user_id
```

### 리뷰

- 누적합을 구하기 위해 윈도우 함수를 사용함
  - `start_date`, `end_date` 를 알려면 group by 를 사용할 수 없음

- Gemini 분석 결과 발견한 문제 ..
  - 날짜가 연속되지 않아도 count가 증가함!!

  - 하루에 정확히 1개 행동을 하는지 검증하지 않음!!

  - `GROUP BY user_id, action` → 유저가 서로 다른 action에서 각각 5일 연속 달성할 경우 둘 다 결과에 출력됨

### 풀이2 - 개선

```sql
WITH ValidDays AS (
    -- 1. 하루에 정확히 1개의 액션만 한 날짜 필터링
    SELECT 
        user_id, 
        action_date, 
        MIN(action) AS action
    FROM activity
    GROUP BY user_id, action_date
    HAVING COUNT(*) = 1
),
StreakGroups AS (
    -- 2. Gaps and Islands 방식으로 연속된 날짜를 묶는 그룹 키(grp) 생성
    SELECT 
        user_id,
        action,
        action_date,
        DATE_SUB(action_date, INTERVAL ROW_NUMBER() OVER (
            PARTITION BY user_id, action 
            ORDER BY action_date
        ) DAY) AS grp
    FROM ValidDays
),
StreakLengths AS (
    -- 3. 그룹별로 연속 일수(streak_length) 및 기간 계산, 5일 이상 필터링
    SELECT 
        user_id,
        action,
        COUNT(*) AS streak_length,
        MIN(action_date) AS start_date,
        MAX(action_date) AS end_date
    FROM StreakGroups
    GROUP BY user_id, action, grp
    HAVING COUNT(*) >= 5
),
MaxStreaks AS (
    -- 4. 한 유저 내에서 최대 연속 길이의 시퀀스 식별
    SELECT 
        user_id,
        action,
        streak_length,
        start_date,
        end_date,
        RANK() OVER (PARTITION BY user_id ORDER BY streak_length DESC) AS rnk
    FROM StreakLengths
)
-- 5. 최종 결과 반환 및 정렬
SELECT 
    user_id,
    action,
    streak_length,
    start_date,
    end_date
FROM MaxStreaks
WHERE rnk = 1
ORDER BY streak_length DESC, user_id ASC;
```

### 리뷰

- **Gaps and Islands 기법**
  - **연속된 데이터 구간**(Islands)과 흐름이 끊기는 단절 구간(Gaps)를 식별하기 위한 패턴

  - 대표적인 방법
    - `Date - ROW_NUMBER()`

    - 날짜가 하루씩 증가할 때, `ROW_NUMBER()` 도 1씩 증가함

    - 두 값의 차이를 구하면 항상 동일한 상수 (특정 날짜)가 도출됨 

    - 흐름이 끊기면 `ROW_NUMBER()`와 날짜의 증가폭이 어긋나기 때문에 도출되는 상수가 달라짐 → 연속된 구간을 하나의 `GROUP BY` 키로 묶어낼 수 있게됨

- `ROW_NUMBER()`
  - 각 행에 고유한 일련번호를 부여함

  - 지정된 파티션 내에서 정렬 기준에 따라 1씩 증가하는 값

  - 정렬 조건이 완벽하게 일치하는 동점 데이터가 들어오더라도 공동 순위를 허용하지 않음 → 반드시 1개의 행만 추출해야 하는 경우 사용

- `RANK()`
  - 데이터의 값을 기준으로 순위를 매김

  - 동점 데이터가 들어올 경우 공동 순위를 매김
    - 공동 순위가 발생한 직후의 행은 동점자 수만큼 수를 건너뛰어 다음 순위를 매김

  - 값의 상대적 격차와 동점자의 존재를 나타낼 때 사용

- 윈도우 함수 종류에 대해 한 번 정리하면 좋을 것 같다 ! 

- 함수 종류와 용도를 익히고 있다면 조금 더 로직을 코드로 표현하기 쉬워질듯