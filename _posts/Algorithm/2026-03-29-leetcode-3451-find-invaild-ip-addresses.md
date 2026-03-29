---
title: "Leetcode) 3451. Find Invalid IP Addresses"
last_modified_at: 2026-03-29T17:25:00+00:00
notion_page_id: 33212b31-a8a8-8024-9bc1-d4bb3adbc97d
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

[https://leetcode.com/problems/find-invalid-ip-addresses/description/](https://leetcode.com/problems/find-invalid-ip-addresses/description/)

Table:  `logs`

```
+-------------+---------+
| Column Name | Type    |
+-------------+---------+
| log_id      | int     |
| ip          | varchar |
| status_code | int     |
+-------------+---------+
log_id is the unique key for this table.
Each row contains server access log information including IP address and HTTP status code.
```

Write a solution to find **invalid IP addresses**. An IPv4 address is invalid if it meets any of these conditions:

- Contains numbers **greater than** `255` in any octet

- Has **leading zeros** in any octet (like `01.02.03.04`)

- Has **less or more** than `4` octets

Return *the result table ordered by* `invalid_count`, `ip` *in ****descending**** order respectively*.

### 풀이

```sql
SELECT 
    ip, 
    COUNT(*) AS invalid_count
FROM logs
WHERE ip NOT REGEXP '^((0|[1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(0|[1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
GROUP BY ip
ORDER BY invalid_count DESC, ip DESC;
```

### 리뷰

- 올바르지 않은 IP → 올바른 IP 규칙으로 변환해서 해당하는 행 찾기

- 정규식
  - 각 옥텟
    - `0`
      - 숫자 0 하나만 있는 경우

    - `[1-9][0-9]?`
      - **1 ~ 99** 구간: 첫자리는 0이 되면 안됨

    - `1[0-9]{2}`
      - **100 ~ 199** 구간: 1로 시작, 뒤에 0~9 숫자가 2개

    - `2[0-4][0-9]`
      - **200 ~ 249** 구간: 2로 시작, 두번째 자리는 0~4만 가능, 세번째 자리는 0~9 가능

    - `25[0-5]`
      - **250 ~ 255** 구간: 마지막 자리는 0~5만 가능

  - 전체 구조
    - `^ 와 $`
      - `^` : 문자열 시작, `$` : 문자열 끝
      - 부분 매칭이 되지 않고 정확히 IP 형태인 것만 통과시키기 위해 사용

    - `((<규칙>)\.){3}`
      - <규칙> 뒤에 . 이 붙은 형태가 정확히 3번({3}) 반복된다는 뜻
      - 정규식 기호 중에서도 `.`이 있기 때문에 역슬래시를 이용해 진짜 점을 의미하도록 함
      - 이 부분은 IP의 A.B.C. 까지를 만들어 냄 (예: 192.168.0.)

    - `마지막 (<규칙>)`
      - IP의 마지막 숫자
      - 끝에 점이 안붙기 때문에 숫자만 추가해주기 위해 규칙을 한 번 더 적어줌