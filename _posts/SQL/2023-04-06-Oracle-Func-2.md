---
title: "[DBP] CH2-2. Oracle 숫자 처리 함수"
last_modified_at: 2023-04-06T17:13:00-05:00
layout: post
categories:
    - SQL
excerpt: OracleDB) Built-in Function/숫자 처리 함수
toc: true
toc_sticky: true
author_profile: true
mathjax: true
---

<br>

## 🍈 숫자 처리 함수
---

<br>

### CEIL
- 소수점에서 올림

```sql
select CEIL(숫자) from dual;
```

```sql
select CEIL(7.6) from dual;
--> 8

select CEIL(0.1) from dual;
--> 1
```

<br>

### FLOOR
- 소수점 버림

```sql
select FLOOR(숫자) from dual;
```

```sql
select FLOOR(6.2) from dual;
--> 6
```

<br>

### MOD
- 값을 나눈 나머지 반환
- 숫자 % 나눌 숫자

```sql
select MOD(숫자, 나눌 숫자) from dual;
```

```sql
select MOD(3, 2) from dual;
--> 1
```

<br>

### POWER
- 제곱 함수
- 숫자1 ^ 숫자2

```sql
select POWER(숫자1, 숫자2) from dual;
```

```sql
select POWER(3, 2) from dual;
--> 9
```

<br>

### ROUND
- 반올림
- 소수 부분, 정수 부분, 날짜 반올림 가능

```sql
select ROUND(숫자, 표시할 자리수) from dual;

-- 소수점 첫째자리에서 반올림
select ROUND(숫자 [, 0]) from dual;

-- 소수점 둘째자리에서 반올림 
select ROUND(숫자, 1) from dual;

-- 소수 부분 버리고 정수 반올림
select ROUND(숫자, -1) from dual;  -- 정수 첫째자리에서 반올림
select ROUND(숫자, -2) from dual;  -- 정수 둘째자리에서 반올림
```

```sql
select ROUND(1235.543) from dual; 
select ROUND(1235.543, 0) from dual;
--> 1236

select ROUND(1235.345, 1) from dual;
--> 1235.3

select ROUND(1235.235, -1) from dual;
--> 1240

select ROUND(1235.345, -3) from dual;
--> 1000
```

<br>

### TRUNC
- 반올림하지 않고 버림

```sql
select TRUNC(숫자, 표시할 자리수) from dual;
```

```sql
select TRUNC(1234.56, 1) from dual;
--> 1234.5

select TRUNC(1234.56, -1) from dual;
--> 1230
```

<br>

### SIGN
- 양수 / 음수 판단
- 양수: `1` 반환
- 음수: `-1` 반환
- 0: `0` 반환
- NULL: `NULL` 반환

```sql
select SIGN(숫자) from dual;
```

```sql
select SIGN(100) from dual;
--> 1

select SIGN(-94) from dual;
--> -1

select SIGN(0) from dual;
--> 0

select SIGN(NULL) from dual;
-->

```