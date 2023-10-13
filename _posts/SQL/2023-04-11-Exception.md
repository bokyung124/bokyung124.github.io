---
title: "[DBP] CH3-4. Exception"
last_modified_at: 2023-04-11T12:35:00-05:00
layout: post
categories:
    - SQL
excerpt: OracleDB) PL/SQL
toc: true
toc_sticky: true
author_profile: true
mathjax: true
---

<br>

## 🌳 예외 종류
---

|예외|설명|처리|
|---|---|---|
|미리 정의된 오라클 서버 예외 </br> (Predefined Exceptions)|PL/SQL에서 자주 발생하는 약 20개의 오류|선언할 필요도 없고, 발생시에 예외 절로 자동 트랩(trap)|
|미리 정의되지 않은 오라클 서버 예외 </br> (Undefined Exceptions)|미리 정의된 오라클 서버 오류를 제외한 모든 오류|선언부에서 선언해야 하고, 발생시 자동 트랩|
|사용자 정의 예외 </br> (User-defined Exceptions)|개발자가 정한 조건에 만족하지 않을 경우 발생하는 오류|선언부에서 선언하고, 실행부에서 RAISE문을 사용하여 발생|

<br>

### 예외 처리 형식
```sql
EXCEPTION
    WHEN exception1 [OR exceptions2 ...] THEN
        statement;
        ...
    [WHEN exception3 [OR exception4 ...] THEN
        statement;
        ...
    ]
    [WHEN OTHERS THEN
        statement;
        ...
    ]
```

<br>

### 주의사항
- WHEN OTHERS 절은 맨 마지막에 위치
- 예외 처리절은 `EXCEPTION`부터 시작
- 여러 개의 예외 처리부 허용
- 예외가 발생하면 여러 개의 예외 처리부 중 하나의 예외 처리부로 트랩 (trap)

<br>

## 🌳 미리 정의된 예외
---

|예외|설명|
|---|---|
|NO_DATA_FOUND|SELECT문이 아무런 데이터 행을 반환하지 못할 때|
|TOO_MANY_ROWS|SELECT문이 하나 이상의 행을 반환할 때|
|INVALID_CURSOR|잘못된 커서 연산|
|ZERO_DIVIDE|0으로 나눌 때|
|DUP_VAL_ON_INDEX|UNIQUE 제약을 갖는 컬럼에 중복되는 데이터가 INSERT 될 때|
|TIMEOUT_ON_RESOURCE|자원을 기다리는 동안 타임 아웃이 발생하는 경우|
|INVALID_NUMBER|숫자 데이터 에러 </br> ex) '3D2'는 숫자가 아님|
|STORAGE_ERROR|메모리 부족으로 발생하는 PL/SQL 에러|
|PROGRAM_ERROR|내부 PL/SQL 에러|
|VALUE_ERROR|숫자의 계산, 변환 또는 버림 등에서 발생하는 에러|
|ROWTYPE_MISMATCH|호스트의 커서 변수와 PL/SQL 커서 변수의 타입이 맞지 않을 때 발생|
|CURSOR_ALREADY_OPEN|이미 열려있는 커서를 다시 열려고 할 때 발생|

<br>

### 예시

```sql
DECLARE 
    v_emp emp%ROWTYPE;
BEGIN
    SELECT empno, ename, deptno
    INTO v_emp.empno, v_emp.ename, v_emp.deptno
    FROM emp
    WHERE deptno = 234;

    DBMS_OUTPUT.PUT_LINE('사번: '||v_emp.empno);
    DBMS_OUTPUT.PUT_LINE('이름: '||v_emp.ename);
    DBMS_OUTPUT.PUT_LINE('부서번호: '||v_emp.deptno);
EXCEPTION
    WHEN DUP_VAL_ON_INDEX THEN
        DBMS_OUTPUT.PUT_LINE('DUP_VAL_ON_INDEX 에러 발생');
    WHEN TOO_MANY_ROWS THEN
        DBMS_OUTPUT.PUT_LINE('TOO_MANY_ROWS 에러 발생');
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('NO_DATA_FOUND 에러 발생');
    WHEN OHTERS THEN
        DBMS_OUTPUT.PUT_LINE('기타 에러 발생');
END;

-- TOO_MANY_ROWS 에러 발생
```

<br>

## 🌳 미리 정의되지 않은 예외
---

### 처리 방법
- 1단계: 예외의 이름을 선언 (선언절)
- 2단계: `PRAGMA EXCEPTION_INIT` 문장으로 예외의 이름과 오라클 서버 오류 번호를 결합 (선언절)
- 3단계: 예외가 발생할 경우 해당 예외를 참조 (예외절)

<br>

### 예시

```sql
DECLARE
    not_null_test EXCEPTION    -- 1단계

    /* not_null_test는 선언된 예외 이름
       -1400 Error 처리 번호는 표준 Oracle Server Error 번호 */
    PRAGMA EXCEPTION_INIT(not_null_test, -1400)     -- 2단계
BEGIN
    -- empno를 입력하지 않아서 NOT NULL 에러 발생
    INSERT INTO emp(ename, deptno)
    VALUES ('tiger', 30);

EXCEPTION
    WHEN not_null_test THEN    -- 3단계
        DMBS_OUTPUT.PUT_LINE('not null 에러 발생');
END;

-- not null 에러 발생
```

<br>

## 🌳 사용자 정의 예외
---

- 오라클 저장함수 `RAISE_APPLICATION_ERROR`를 사용하여 오류코드 -20000부터 -20999의 범위 내에서 사용자 정의 예외 만들 수 있음

<br>

### 처리 방법
- 1단계: 예외 이름 선언 (선언절)
- 2단계: `RAISE`문을 이용하여 직접적으로 예외 발생 (실행절)
- 3단계: 예외가 발생할 경우 해당 예외 참조 (예외절)

<br>

### 예시
```sql
DECLARE
    -- 예외 이름 선언 
    user_define_error EXCEPTION;    -- 1단계
    cnt NUMBER:
BEGIN
    SELECT COUNT(empno)
    INTO cnt
    FROM emp
    WHERE deptno = 234;

    IF cnt < 5 THEN
        -- RAISE문을 사용하여 직접적으로 예외 발생
        RAISE user_define_error;   -- 2단계
    END IF;
EXCEPTION
    -- 예외 발생 시 해당 예외 참조
    WHEN user_define_error THEN    -- 3단계
        RAISE_APPLICATION_ERROR(-20001, '사원 부족');
END;
```

<br>

## 🌳 SQLCODE, SQLERRM
---

- `WHEN OTHERS`문으로 트랩되는 오류들의 실제 오류 코드와 설명을 볼 때 사용
- SQLCODE
    - 실행된 프로그램이 성공적으로 종료했을 때는 오류번호 0을 포함하며, 그렇지 않을 경우에는 해당 오류코드 번호 포함
- SQLERRM
    - SQLCODE에 포함된 오라클 오류번호에 해당하는 메시지 가짐

<br>

|SQLCODE 값|설명|
|---|---|
|0|오류 없이 성공적으로 종료|
|1|사용자 정의 예외 번호|
|+100|NO_DATA_FOUND 예외 번호|
|음수| 위의 것을 제외한 오라클 서버 에러 번호|

<br>

### 예시
```sql
DECLARE
    v_emp emp%ROWTYPE;
BEGIN
    SELECT *
    INTO v_emp
    FROM emp;

    DBMS_OUTPUT.PUT_LINE('사번: '||v_emp.empno);
    DBMS_OUTPUT.PUT_LINE('이름: '||v_emp.ename);
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('ERR CODE: '||TO_CHAR(SQLCODE));
        DBMS_OUTPUT.PUT_LINE('ERR MESSAGE: '||SQLERRM);
END;


/*
ERR CODE: -1422
ERR MESSAGEL ORA-01422 : exact fetch returns more than requested number of rows
PL/SQL procedure successfully completed.
*/
```