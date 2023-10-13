---
title: "[DBP] CH4-1. PL/SQL - Procedure"
last_modified_at: 2023-04-20T13:01:00-05:00
layout: post
categories:
    - SQL
excerpt: OracleDB) Procedure
toc: true
toc_sticky: true
author_profile: true
mathjax: true
tag: [lecture, OracleSQL]
---

<br>

## 🍯 프로시저
---

## 개요
- 매개 변수를 받을 수 있고, 반복해서 사용할 수 있는 이름이 있는 PL/SQL 블록
- return 값이 없음
- 연속 실행 또는 구현이 복잡한 트랜잭션을 수행하는 PL/SQL 블록을 DB에 저장하기 위해 생성

<br>

### 형식
- `CREATE OR REPLACE` 구문을 이용하여 생성
- `IS`로 PL/SQL 블록 시작
- LOCAL 변수는 `IS`와 `BEGIN` 사이에 선언

<br>

```sql
CREATE [OR REPLACE] procedure name
    [(IN argument
      OUT argument
      IN OUT argument)]  -- 매개변수
IS
    [변수/커서 선언]
BEGIN    -- 필수
    [PL/SQL Block]  
        -- SQL 문장, PL/SQL 제어 문장

    [EXCEPTION]   -- 선택
        -- error가 발생할 때 수행하는 문장
END;     -- 필수
```

<br>

## 🍯 파라미터
---

### 특징
- 실행 환경과 프로그램 사이에 값을 주고 받는 역할
- 블록 안에서의 변수와 똑같이 일시적으로 값을 저장하는 역할

<br>

### 종류
- `IN`
    - 실행환경에서 프로그램으로 값 전달
    - 상수, 수식, 또는 초기화된 변수 사용
    - default, `IN` 키워드 생략 가능
- `OUT`
    - 프로그램으로부터 실행환경으로 값 전달
    - 초기화되지 않은 변수를 매개변수로 사용
    - 반드시 지정
- `INOUT`
    - 실행환경에서 프로그램으로 값을 전달하고, 다시 프로그램으로부터 실행환경으로 변경된 값 전달
    - 초기화된 변수 사용
    - 반드시 지정

<br>

## 🍯 프로시저의 생성과 실행
---

- 생성
    - `CREATE OR REPLACE` 구문을 이용하여 생성
    - 프로시저를 끝마칠 때는 `/` 지정
- 실행
    - `EXECUTE 프로시저명;`
- 프로시저 에러 검사
    - `SHOW ERROR`
- 삭제
    - `DROP PROCEDURE 프로시저명`

<br>

## 🍯 프로시저 예
---

### 생성
```sql
CREATE OR REPLACE PROCEDURE update_sal
    /* IN Parameter*/
    (v_empno IN NUMBER)
IS
BEGIN
    UPDATE emp
    SET sal = sal * 1.1
    WHERE empno = v_empno;

    COMMIT;
END;
/
```

<br>

### 에러 검사
```sql
SHOW ERROR
-- No errors.
```

<br>

### 실행
```sql
EXECUTE update_sal(7369);
-- PL/SQL 처리가 정상적으로 완료되었습니다.
```