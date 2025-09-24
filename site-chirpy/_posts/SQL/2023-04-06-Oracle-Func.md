---
title: "[DBP] CH2-1. Oracle 문자 처리 함수"
last_modified_at: 2023-04-06T15:23:00-05:00
layout: post
categories:
    - SQL
excerpt: OracleDB) Built-in Function/문자 처리 함수
toc: true
toc_sticky: true
author_profile: true
mathjax: true
tag: [lecture, OracleSQL]
---


## 🍈 문자 처리 함수


### CHR 
- 숫자 -> 해당 ASCII 값에 해당하는 문자 반환

```sql 
select CHR(숫자) from dual;
```
```sql
select CHR(65) from dual;
--> A
```

<br>

### ASCII
- 문자 -> ASCII 코드 값 반환

```sql
select ASCII('문자') from dual;
```   
```sql
select ASCII('7') from dual;
--> 55

select ASCII('A') from dual;
--> 65 
``` 

<br>

### LOWER / UPPER
- 소문자 / 대문자로 변환

```sql
select LOWER('문자') from dual;
select UPPER('문자') from dual;
```

```sql
select LOWER('ORACLE') from dual;
--> oracle

selece UPPER('oracle') from dual;
--> ORACLE
```

<br>

### INITCAP
- 첫 글자만 대문자로 변환

```sql 
select INITCAP('문자') from dual;
```

```sql
select INITCAP('oracle') from dual;
--> Oracle
```

<br>

### LPAD 
- 문자열 오른쪽 정렬 후 왼쪽 공백에 문자 삽입

```sql
select LPAD('문자열', 문자열 총 길이, '공백 채울 문자') from dual;
```

```sql
select LPAD('HI', 10, '*') from dual;
--> ********HI
```

<br>

### RPAD
- 문자열 왼쪽 정렬 후 오른쪽 공백에 문자 삽입

```sql
select RPAD('문자열', 문자열 총 길이, '공백 채울 문자') from dual;
```

```sql
select RPAD('WOW', 5, '-') from dual;
--> WOW--

select RPAD(SUBSTR('011124-1234567', 1, 7), 14, '*') from dual;
--> 011124-*******
```

<br>

### LTRIM
- 왼쪽 특정 문자(공백) 삭제   
- 인수로 `문자열`만 넣으면 공백 삭제

```sql
select LTRIM('문자열', '삭제할 문자') from dual;
```

```sql
select LTRIM('Oracle', 'O') from dual;
--> racle

select LTRIM('    HAPPY') from dual;
--> HAPPY
```

<br>

### RTRIM
- 오른쪽 특정 문자(공백) 삭제   
- 인수로 `문자열`만 넣으면 공백 삭제

```sql
select RTRIM('문자열', '삭제할 문자') from dual;
```

```sql
select RTRIM('Oracle', 'e') from dual;
--> Oracl

select RTRIM('HAPPY    ') from dual;
--> HAPPY
```

<br>

### REPLACE
- 문자열 치환   
- `치환하여 넣을 문자` 인수로 넣지 않으면 특정 문자 제거

```sql
select REPLACE('문자열', '없앨 문자열', '치환하여 넣을 문자열') from dual;
```

```sql
select replace('oracle database', 'database', 'db') from dual;
--> oracle db

select replace('oracle database', 'database') from dual;
--> oracle
```

<br>

### SUBSTR / SUBSTRB
- 문자열 일부분 반환   
- `SUBSTRB`는 Byte 기준   
- 인덱스는 **1**부터 시작

```sql
-- 특정 지점부터 끝까지 반환
select SUBSTR('문자열', 시작할 인덱스) from dual;

-- 일정 부분만 잘라서 반환
select SUBSTR('문자열', 시작 인덱스, 길이) from dual;

-- 뒤에서부터 자르기
select SUBSTR('문자열', 시작 인덱스(음수) [, 길이]) from dual;

-- byte 단위로 자르기
-- 한글 3byte / 2byte
select SUBSTRB('문자열', 시작 인덱스, 길이) from dual;
```

```sql
select SUBSTR('Hello World!', 3) from dual;
--> llo World!

select SUBSTR('Hello World!', 3, 5) from dual;
--> llo W

select SUBSTR('Hello World!', -4) from dual;
--> rld!

select SUBSTRB('안녕하세요', 4, 6) from dual;
--> 녕하
```

<br>

### LENGTH / LENGTHB
- 문자열 길이 반환   
- `LENGTHB`는 Byte 길이

```sql
select LENGTH('문자열') from dual;

select LENGTHB('문자열') from dual;
```

```sql
select LENGTH('Hello') from dual;
--> 5

select LENGTH('오라클 DB') from dual;
--> 6

select LENGTHB('하이') from dual;
--> 6
```

<br>

### INSTR / INSTRB
- 문자열 위치 반환   
- 찾는 문자가 없으면 `0` 반환   
- 찾는 단어 앞 글자의 인덱스 반환   
- 끝에서 부터 찾으려면 **음수** 입력   

```sql
select INSTR('문자열', '찾는 문자열' [, 시작지점, 몇번째 단어 반환할지]) from dual;
```

```sql
select INSTR('HAPPY BIRTHDAY', 'YOU') from dual;
--> 0

select INSTR('HAPPY BIRTHDAY', 'BI') from dual;
--> 6

select INSTR('HAPPY BIRTHDAY', 'Y', 6) from dual;
--> 15  
-- (6번째부터 찾기 시작)

select INSTR('HAPPY BIRTHDAY', 'P', 2, 2) from dual;
--> 4  
-- (2번째부터 시작해서 나오는 값 중에 2번째 값의 위치 반환)

select INSTR('HAPPY BIRTHDAY', 'A', -1, 1) from dual;
--> 14
-- (뒤에서 첫번째 글자부터 찾기 시작하여 첫번째로 나오는 값의 위치)
```