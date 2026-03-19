---
title: "Leetcode) 570. Managers with at Least 5 Direct Reports"
last_modified_at: 2026-03-19T13:45:00+00:00
notion_page_id: 32812b31-a8a8-8062-acf3-d809f784a9f5
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

[https://leetcode.com/problems/managers-with-at-least-5-direct-reports/description/?envType=study-plan-v2&envId=top-sql-50](https://leetcode.com/problems/managers-with-at-least-5-direct-reports/description/?envType=study-plan-v2&envId=top-sql-50)

```plain text
+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| id          | int     |
| name        | varchar |
| department  | varchar |
| managerId   | int     |
+-------------+---------+
id is the primary key (column with unique values) for this table.
Each row of this table indicates the name of an employee, their department, and the id of their manager.
If managerId is null, then the employee does not have a manager.
No employee will be the manager of themself.
```

Write a solution to find managers with at least **five direct reports**.

Return the result table in **any order**.

The result format is in the following example.

### 풀이 1 - CTE

```sql
WITH m AS (
    SELECT managerid, count(*)
    FROM employee
    GROUP BY managerid
    HAVING count(*) >= 5
)
SELECT name
FROM employee e
JOIN m ON e.id = m.managerid
```

### 리뷰

- join이 그나마 로직 생각하기 쉬워서인지 이 방식이 먼저 생각나는 경우가 많은 것 같음
  - 다른 방법으로 풀 수 있는지도 계속 고민하기!

### 풀이 2 - 서브쿼리

```sql
SELECT name
FROM employee
WHERE id IN (
    SELECT managerid
    FROM employee
    GROUP BY managerid
    HAVING count(*) >= 5
)
```

### 리뷰

- `FROM id IN` 이 계속 생각이 안나서 은근히 고민했던 문제
  - 위 CTE 방식을 살펴보면 간단히 서브쿼리로 바꿀 수 있다는걸 알 수 있음

- 지난 문제에서 SQL 실행 로직 (FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY) 을 다시 상기시키니 로직 생각하기가 더 쉬웠음