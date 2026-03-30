---
title: "Leetcode) 585. Investments in 2016"
last_modified_at: 2026-03-30T07:35:00+00:00
notion_page_id: 33312b31-a8a8-8039-b8e8-df0b1918e211
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

[https://leetcode.com/problems/investments-in-2016/description/?envType=study-plan-v2&envId=top-sql-50](https://leetcode.com/problems/investments-in-2016/description/?envType=study-plan-v2&envId=top-sql-50)

Table: `Insurance`

```
+-------------+-------+
| Column Name | Type  |
+-------------+-------+
| pid         | int   |
| tiv_2015    | float |
| tiv_2016    | float |
| lat         | float |
| lon         | float |
+-------------+-------+
pid is the primary key (column with unique values) for this table.
Each row of this table contains information about one policy where:
pid is the policyholder's policy ID.
tiv_2015 is the total investment value in 2015 and tiv_2016 is the total investment value in 2016.
lat is the latitude of the policy holder's city. It's guaranteed that lat is not NULL.
lon is the longitude of the policy holder's city. It's guaranteed that lon is not NULL.
```

Write a solution to report the sum of all total investment values in 2016 `tiv_2016`, for all policyholders who:

- have the same `tiv_2015` value as one or more other policyholders, and

- are not located in the same city as any other policyholder (i.e., the (`lat, lon`) attribute pairs must be unique).

Round `tiv_2016` to **two decimal places**.

### 풀이1 - 서브쿼리

```sql
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM insurance i
WHERE tiv_2015 IN (SELECT tiv_2015 FROM insurance t WHERE i.pid != t.pid)
AND CONCAT(lat, ',', lon) NOT IN (SELECT CONCAT(lat, ',', lon) FROM insurance s WHERE i.pid != s.pid)
```

### 리뷰

- **다른 사용자** 와 비교하기 위해 서브 쿼리 사용

- 그냥 `CONCAT(lat, lon)` 을 사용하면 `lat=1, lon=23` 인 경우와 `lat=12, lon=3` 인 경우가 동일한 경우가 됨! 중간에 쉼표를 넣어주어서 lat과 lon을 구분해주어야 했음


### 풀이2 - 윈도우 함수

```sql
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM (
    SELECT tiv_2016,
           COUNT(*) OVER(PARTITION BY tiv_2015) AS cnt_tiv_2015,
           COUNT(*) OVER(PARTITION BY lat, lon) AS cnt_location
    FROM insurance
) t
WHERE cnt_tiv_2015 > 1 AND cnt_location = 1;
```

### 리뷰

- 행마다 비교하는 것이 아니라, 현재 행과 같은/다른 행의 **개수** 를 세서 비교하는 방식!!

- **기존 방식 (Nested Loop)**:
  - 1번 행을 잡고 -> 전체 테이블을 다 뒤져서 같은 tiv_2015가 있는지 확인

  - 2번 행을 잡고 -> 또 전체 테이블을 다 뒤져서 확인...

- **윈도우 함수 방식 (Sort/Hash)**:
  - 데이터를 tiv_2015 기준으로 정렬하거나 해시 지도를 만듦

  - **한 번 쓱 훑으면서** 각 그룹에 몇 개가 있는지 적어둠

  - 데이터가 1만 건이어도 **단 몇 번의 스캔**만으로 계산이 끝남