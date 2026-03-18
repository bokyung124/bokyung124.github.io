---
title: "Leetcode) 3673. Find Zombie Sessions"
last_modified_at: 2026-03-18T17:39:00+00:00
notion_page_id: 32712b31-a8a8-80a1-8006-d427a71b5540
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

[https://leetcode.com/problems/find-zombie-sessions/description/](https://leetcode.com/problems/find-zombie-sessions/description/)

Write a solution to identify **zombie sessions, **sessions where users appear active but show abnormal behavior patterns. A session is considered a **zombie session** if it meets ALL the following criteria:

- The session duration is **more than** `30` minutes.

- Has **at least** `5` scroll events.

- The **click-to-scroll ratio** is less than `0.20` .

- **No purchases** were made during the session.

Return *the result table ordered by* `scroll_count` *in ****descending**** order, then by* `session_id` *in ****ascending**** order*.

### 풀이1 - CTE

```sql
WITH execute_table AS (
    SELECT 
        session_id, 
        TIMESTAMPDIFF(MINUTE, MIN(event_timestamp), MAX(event_timestamp)) AS session_duration_minutes,
        SUM(event_type = 'scroll') AS scroll_count,
        SUM(event_type = 'click') AS click_count,
        SUM(event_type = 'purchase') AS purchase_count
    FROM app_events
    GROUP BY session_id
)
SELECT a.session_id, MAX(user_id) AS user_id, session_duration_minutes, scroll_count
FROM app_events a
JOIN execute_table e ON a.session_id = e.session_id
WHERE e.session_duration_minutes >= 30
	AND e.scroll_count >= 5
	AND e.purchase_count = 0
	AND e.click_count / e.scroll_count < 0.2
GROUP BY a.session_id
ORDER BY e.scroll_count DESC, a.session_id
```

### 리뷰

- 시간 **차이**를 구할 땐 `TIMESTAMPDIFF` 사용
  - `MINUTE(MAX(timestamp) - MIN(timestamp))` 
→ 만약 세션 시작 시간이 10:00 이고 종료 시간이 11:15 라면, 두 시간의 차이는 총 **75분이지만,** MINUTE를 쓰면 75분이 아니라 **15**만 반환하게 됨.

- MySQL에서는 괄호 안의 조건이 참(True)이면 1, 거짓(False)이면 0을 반환 → `SUM()` 을 사용하면 특정 이벤트의 개수를 간결하게 구할 수 있음!
  - PostgreSQL 등에서는 `SUM` 과 `CASE` 를 같이 사용하여 이벤트 개수를 구할 수 있음
    ```sql
    SUM(CASE WHEN event_type = 'scroll' THEN 1 ELSE 0 END) AS scroll_count
    ```


### 풀이2 - HAVING

```sql
SELECT 
    session_id, 
    MAX(user_id) AS user_id, 
    TIMESTAMPDIFF(MINUTE, MIN(event_timestamp), MAX(event_timestamp)) AS session_duration_minutes,
    SUM(event_type = 'scroll') AS scroll_count
FROM app_events
GROUP BY session_id
HAVING 
    session_duration_minutes >= 30
    AND SUM(event_type = 'scroll') >= 5 
    AND SUM(event_type = 'click') / SUM(event_type = 'scroll') < 0.2
    AND SUM(event_type = 'purchase') = 0 
ORDER BY scroll_count DESC, session_id;
```

### 리뷰

- `HAVING`
  - `GROUP BY` 가 끝난 뒤, 그룹을 필터링할 때 사용

  - CTE를 사용했을 땐 이미 `GROUP BY` 로 뭉친 테이블에서 조회를 하기 때문에 `WHERE` 절 사용함 

- SQL 실행 순서
  - **FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY**

- 이 방식이 100ms 더 빨랐음