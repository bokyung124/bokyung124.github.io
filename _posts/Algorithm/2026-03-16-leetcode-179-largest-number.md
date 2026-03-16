---
title: "Leetcode) 179. Largest Number"
last_modified_at: 2026-03-16T01:32:00+00:00
notion_page_id: 32512b31-a8a8-8082-95e7-fed88e3a7cd9
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

[https://leetcode.com/problems/largest-number/description/](https://leetcode.com/problems/largest-number/description/)

### 문제

Given a list of non-negative integers `nums`, arrange them such that they form the largest number and return it.

Since the result may be very large, so you need to return a string instead of an integer.

**Example 1:**

```plain text
Input: nums = [10,2]
Output: "210"
```

**Example 2:**

```plain text
Input: nums = [3,30,34,5,9]
Output: "9534330"
```

**Constraints:**

- `1 <= nums.length <= 100`

- `0 <= nums[i] <= 109`

### 풀이

```python
from functools import cmp_to_key

class Solution:
    def largestNumber(self, nums: List[int]) -> str:
        nums_str = list(map(str, nums))
        nums_str.sort(key=cmp_to_key(lambda a, b: -1 if a+b > b+a else 1))
        return str(int(''.join(nums_str)))
```

### 유형

`**커스텀 정렬**`

- 기본 오름/내림차순 외에 구조체, 특정 조건(예: 절댓값, 문자열 길이)을 기준으로 데이터를 정렬하는 방식

- 단일 기준은 `key` 함수로, 두 원소를 이어붙여 비교하는 등 복잡한 기준은 `cmp_to_key` 로 비교 함수 작성

`**sorted() / list.sort()**`** **

- 내장 함수

- key 매개변수에 lambda 함수를 전달하여 커스텀 정렬 기준 정의 

- 다중 기준 정렬도 가능 (튜플 key 사용)

- 같은 key의 원소는 원래 순서가 유지됨

- `list.sort(key=lambda x: (-x[1], x[0]))`

`**functools.cmp_to_key**`

- functools 라이브러리 함수

- 두 원소를 직접 비교하는 비교 함수를 key 함수로 변환

- 이어붙이기 비교처럼 단순 key로 표현하기 어려운 경우에 사용

- 문자열 내림차순은 이 함수 사용