---
title: "[DBP] CH2-3. Oracle 기타 내장 함수"
last_modified_at: 2023-04-06T18:06:00-05:00
layout: post
categories:
    - SQL
excerpt: OracleDB) Built-in Function/날짜 함수, 변환 함수, 기타 함수
toc: true
toc_sticky: true
author_profile: true
mathjax: true
tag: [lecture, OracleSQL]
---

<br>

## 🍈 날짜 처리 함수
---

### SYSDATE
- 현재 날짜와 시간 반환
- format 변경
    - `TO_CHAR(SYSDATE, HH24:MI:SS')` : 24시간 포맷으로 시간만 반환
    - `TO_CHAR(SYSDATE, HH:MI:SS')` : 12시간 포맷으로 시간만 반환
    - `TO_CHAR(SYSDATE, 'YYYYMMDD')` : 날짜만 반환

```sql
select SYSDATE from dual;
--> 06-APR-23
```

<br>

##E LAST_DAY
- 해당 월의 마지막 날짜

```sql
select LAST_DAY(날짜) from dual;
```

```sql
select LAST_DAY(TO_DATE('2023-01-15', 'YYYY-MM-DD')) from dual;
--> 31-JAN-23
```

#### 달의 시작 일자 구하기
- `TRUNC(날짜, 'MM')`

```sql
select TRUNC(SYSDATE, 'MM') from dual;
--> 01-APR-23
```

<br>

### MONTHS_BETWEEN
- 두 기간 사이의 개월 수 

```sql
select MONTHS_BETWEEN(날짜1, 날짜2) from dual;
```

```sql
select MONTHS_BETWEEN(SYSDATE, TO_DATE('2022-04-06', 'YYYY-MM-DD')) from dual;
--> 12

select MONTHS_BETWEEN(SYSDATE, TO_DATE('2021-08-30', 'YYYY-MM-DD')) from dual;
--> 19.2385779
-- 1개월 미만의 일 수는 소수점으로 표시
-- TRUNC() 함수로 개월 수만 표현할 수 있음
```

<br>

### ADD_MONTHS
- 날짜의 월 더하거나 빼기
- 바뀐 달에 해당 일자가 없으면 해당 월의 마지막 일자 반환 
    - ex) 2019-03-31 의 이전달은 2019-02-28

```sql
select ADD_MONTHS(날짜, 숫자) from dual;
```

```sql
select ADD_MONTHS(TO_DATE('2021-12-16', 'YYYY-MM-DD'), -1) from dual;
--> 16-NOV-21

select ADD_MONTHS(TO_DATE('2021-12-16', 'YYYY-MM-DD'), 1) from dual;
--> 16-JAN-22
```

### NEXT_DAY
- 다음 첫번째 오는 해당 요일의 날짜
- 월요일
    - 2
    - 월요일
    - 월
    - MONDAY
    - MON

```sql
select NEXT_DAY(기준일자, 찾는요일) from dual;
```

```sql
select NEXT_DAY(SYSDATE, 1) from dual;
--> 09-APR-23
```

<br>

## 🍈 변환 함수
---

### TO_CHAR
- 날짜, 숫자 등의 값을 문자열로 변환

<br>

#### 날짜 포맷 변경
```sql 
select TO_CHAR(SYSDATE, 'YYYYMMDD')               -- 20230406
     , TO_CHAR(SYSDATE, 'YYYY/MM/DD')             -- 2023/04/04
     , TO_CHAR(SYSDATE, 'YYYY-MM-DD')             -- 2023-04-06
     , TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS')  -- 2023-04-04 10:30:23
from dual;
```
- `YYYY`: 년, `MM`: 월, `DD`: 일, `HH24`: 24시간, `HH`: 12시간, `MI`: 분, `SS`: 초

<br>

#### 소수점 변경
```sql
select TO_CHAR(123.456, 'FM990.999')  -- 123.456
     , TO_CHAR(1234.56, 'FM9990.99')  -- 1234.56
     , TO_CHAR(0.12345, 'FM9990.99')  -- 0.12
from dual;
```
- `FM`: 문자열의 공백제거

<br>

#### 지정한 길이만큼 `0`으로 채우기
```sql
select TO_CHAR(123)             -- 123
     , TO_CHAR(123, 'FM00000')  -- 00123
from dual;
```

<br>

### TO_NUMBER
- 숫자로 변환

```sql
select TO_NUMBER('숫자형식의 문자열') from dual;
```

<br>

### TO_DATE
- 문자열을 날짜로 변환

```sql
select TO_DATE('문자열', '날짜포맷') from dual;
```

```sql
select TO_DATE('2021-12-12', 'YYYY-MM-DD')
     , TO_DATE('2021-12-12 17:10:00', 'YYYY-MM-DD HH24:MI:SS')
from dual;
--> 12-DEC-21
```

<br>

## 🍈 기타 함수
---

### NVL
- NULL 처리 함수

```sql
NVL('값', '지정값')
```

- 값이 NULL이면 지정값을 출력하고, 아니면 원래 값 그대로 출력
- NULL 데이터가 존재하여 연산이 불가능한 경우 방지

<br>

#### NVL2
```sql
NVL2('값', '지정값1', '지정값2')
```

- 값이 NULL이 아니면 지정값1을, NULL이면 지정값2를 출력

<br>

### DECODE
- `DECODE(A, B, X, Y)`  
    - A = B 이면 X 출력
    - A ≠ B 이면 Y 출력

- `DECODE(A, B, X, C, Y, Z)`
    - A = B 이면 X 출력
    - A = C 이면 Y 출력
    - A ≠ B 이고, A ≠ C이면 Z 출력

- `DECODE(A1, B, DECODE(A2, C, X, Y), Z)`
    - A1 = B 이면서 A2 = C 이면 X 출력
    - A1 = B 이면서 A2 ≠ C 이면 Y를 출력
    - A1 ≠ B 이면 Z 출력

- B, C, X, Y, Z 자리에 `NULL`도 가능

<br>

### GREATEST / LEAST
- 같은 행에서 **다른 칼럼과 비교하여** 최대값, 최소값 반환

```sql
select GREATEST(100, 200, 300, 400, 500) from dual;
--> 500

select LEAST(100, 200, 300, 400, 500) from dual;
--> 100

select GREATEST('AAA', 'BBB', 'CCC', 'DDD') from dual;
--> DDD

select GREATEST(SYSDATE, SYSDATE + 1, SYSDATE + 2)
from dual;
--> 08-APR-23
```

- **주의** 
    - 값 중 `NULL`이 있으면 무조건 NULL이 반환되므로 변환하고 적용해야 함
    - 다른 유형의 인자값이 섞여있을 경우 오류 발생 (숫자와 문자형 숫자 제외)