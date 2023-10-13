---
title: "[DBP] CH5. PL/SQL - 수강신청 시스템 실습"
last_modified_at: 2023-04-20T13:01:00-05:00
layout: post
categories:
    - SQL
excerpt: OracleDB) Enrollment 
toc: true
toc_sticky: true
author_profile: true
mathjax: true
tag: [lecture, OracleSQL]
---

<br>

## 📋 수강신청 입력
---

### 프로시저 및 함수 적용

- 수강신청 입력 시 **예외 처리**가 많음
    - 이를 프로시저와 함수를 이용하여 작성
    - 수강신청 입력 시 복잡한 예외 처리를 그 때마다 할 필요 없이, 프로시저와 함수를 이용하여 쉽게 처리 가능

<br>

### 수강신청 입력 요구사항 리뷰
- actor: 학생
- 선행조건: 로그인
- 주요 흐름
    - 시스템은 아직 수강 신청하지 않은 과목들을 학생에게 보여줌
    - 학생은 수강 신청하고자 하는 과목 선택
    - 시스템은 선택된 과목을 수강 신청된 것으로 등록
        - 이때, 시스템은 최대학점을 초과했는지 `E-1`, 동일한 과목을 신청했는지 `E-2`, 해당 과목에 대한 수강 신청 인원이 초과되었는지 `E-3`, 
        동일한 시간의 다른 과목이 이미 수강 신청되었는지 `E-4` 검사
- 수강신청 연도와 학기에 대한 요구사항
    - 수강신청 연도와 학기는 현재 날짜가 11월, 12월인 경우에는 다음년도 1학기인 것으로,
    - 1~4월인 경우는 현재 년도 1학기로, 
    - 5~10월은 현재 년도 2학기인 것으로 함

<br>

#### 예외 흐름
- E-1
    - 시스템은 선택된 과목에 따라 총 수강 신청한 과목의 학점이 18학점이 초과되는지 검사
    - 18학점을 초과하면, 시스템은 수강 신청이 될 수 없음을 알림
- E-2
    - 시스템은 선택된 과목이 이미 수강 신청된 과목인지 검사
    - 이미 수강 신청된 과목인 경우, 시스템은 수강 신청이 될 수 없음을 알림
- E-3
    - 시스템은 해당 괌고에 대한 수강 신청 인원이 초과되었는지 검사
    - 수강 신청 인원이 초과된 과목인 경우, 시스템은 수강 신청이 될 수 없음을 알림
- E-4
    - 시스템은 동일한 시간의 다른 과목이 이미 수강 신청 되었는지 검사
    - 동일한 시간의 다른 과목을 이미 신청한 경우, 시스템은 수강 신청이 될 수 없음을 알림

<br>

## 📋 수강신청 입력 프로시저: InsertEnroll
---

### InsertEnroll(p1, p2, p3, p4)
- `IN` 파라미터
    - p1: 학번
    - p2: 과목번호
    - p3: 분반
- `OUT` 파라미터
    - p4: 입력 결과 메시지
        - 수강신청 등록이 완료되었습니다.
        - 최대학점을 초과하였습니다.
        - 이미 등록된 과목을 신청하였습니다.
        - 수강신청 인원이 초과되어 등록이 불가능합니다.
        - 이미 등록된 과목 중 중복되는 시간이 존재합니다.
        - 그 외 에러: SQLCODE(OR SQLERRM)
- 결과
    - 예외 흐름이 아닌 경우, 'enroll' 테이블에 해당 학번, 과목번호, 분반, 수강 연도, 수강 학기가 입력됨
    - 예외가 발생한 경우, 오류 메시지를 보내고 테이블에 입력되지 않음

<br>

### 수강신청 관련 함수

- Date2EnrollYear(p1)
    - `IN` 파라미터
        - p1: 오늘 날짜
    - 리턴 결과
        - 숫자형
        - 수강신청하는 연도 리턴

- Date2EnrollSemester(p1)
    - `IN` 파라미터
        - p1: 오늘 날짜
    - 리턴 결과
        - 숫자형
        - 수강신청하는 학기 리턴

<br>

### InsertEnroll.sql

<script src="https://gist.github.com/bokyung124/8f79a452417e45634dc6b111144f7883.js"></script>

<br>

### function.sql

<script src="https://gist.github.com/bokyung124/d4a57e451b221c8c55233e2fd951ef88.js"></script>

<br>

## 📋 수강신청 결과 확인 : 프로시저
---

- **명시적 커서**를 이용한 프로시저 실습

### SelectTimeTable(p1, p2, p3)
- `IN` 파라미터
    - p1: 학번
    - p2: 연도
    - p3: 학기
- 결과
    - 파라미터로 입력한 학번, 연도, 학기에 해당하는 수강신청 시간표 보여줌
        - 시간표 정보로 교시, 과목번호, 과목명, 분반, 학점, 장소 보여줌
        - 총 신청 과목 수와 총 학점 보여줌

<br>

### verify_enroll.sql

<!-- ```sql
create or replace procedure SelectTimeTable (sStudentId IN VARCHAR2,
                                             nYear IN NUMBER,
                                             nSemester IN NUMBER)
is
    nPeriod number := 1;
    pCourseId course.c_id%TYPE;
    pCourseName course.c_name%TYPE;       -- 변수명 확인
    pCourseIdNo course.c_id_no%TYPE;
    pCourseUnit course.c_unit%TYPE;
    pLocation teach.t_location%TYPE;      -- 변수명 확인
    
begin
    dbms_output.put_line(nYear || '년도 ' || nSemester || '학기의 ' || sStudentId || '님의 수강신청 시간표입니다.');

    loop

    
end;    
``` -->

<script src="https://gist.github.com/bokyung124/aa688fb1eac6a665b8a0b80e3986a6af.js"></script>


<br>

## 📋 수강신청 입력 및 입력 후 결과 확인
---

- InsertEnroll() 프로시저의 입력 결과 확인
    - InsertEnroll() 프로시저 호출
        - 과목번호 'C400' 입력: 동일 과목 신청 오류 발생
        - 과목번호 'C900' 입력: 수강신청 인원 초과 오류 발생
        - 과목번호 'M100' 입력: 신청한 과목들 시간 중복 발생
        - 과목번호 'C800' 입력: 정상적 입력
        - 과목번호 'M700' 입력: 최대 학점 초과 오류 발생
    - 입력 후 결과 확인
        - SelectTimeTable() 프로시저 호출

<br>

### InsertTest.sql

<script src="https://gist.github.com/bokyung124/a953da7ac3248c5c0dea7c448629ec6c.js"></script>

<br>

#### InsertTest.sql 실행 결과

```sql
> @InsertTest

/*

'************ Insert 및 에러 처리 테스트 ************'   
#
20011234님이 과목번호 C400, 분반 3의 수강 등록을 요청하였습니다. 결과 : 이미 등록된 과목을 신청하였습니다.
#
20011234님이 과목번호 C900, 분반 3의 수강 등록을 요청하였습니다. 결과 : 수강신청 인원이 초과되어 등록이 불가능합니다.
#
20011234님이 과목번호 M100, 분반 3의 수강 등록을 요청하였습니다. 결과 : 이미 등록된 과목 중 중복되는 시간이 존재합니다.
#
20011234님이 과목번호 C800, 분반 3의 수강 등록을 요청하였습니다. 결과 : 최대학점을 초과하였습니다.
#
20011234님이 과목번호 M700, 분반 3의 수강 등록을 요청하였습니다. 결과 : 최대학점을 초과하였습니다.

***************** CURSOR를 이용한 SELECT 테스트 ****************
#
2004년도 1학기의 20011234님의 수강신청 시간표입니다.
교시:1, 과목번호:C600, 과목명:소프트웨어 공학, 분반:3, 학점:3, 장소:인- 309
교시:2, 과목번호:C300, 과목명:알고리즘, 분반:3, 학점:3, 장소:인-416
교시:3, 과목번호:C500, 과목명:운영체제, 분반:3, 학점:3, 장소:인-201
교시:4, 과목번호:C700, 과목명:네트워크, 분반:3, 학점:3, 장소:인-310
교시:6, 과목번호:C400, 과목명:데이터베이스, 분반:3, 학점:3, 장소:인-201
교시:7, 과목번호:C800, 과목명:데이터베이스 프로그래밍, 분반:3, 학점:3, 장소:인-309
총 6 과목과 총 18학점을 신청하였습니다.

PL/SQL procedure successfully completed.

*/
```

<br>

## 📋 사용자 정보 수정: 트리거 적용
---

- 사용자 정보 수정시 패스워드에 대한 부분의 처리
    - 참조 무결성과 데이터 무결성 그 밖의 다른 제약 조건으로 정의할 수 없는 복잡한 요구 사항에 대한 제약 조건
    - **트리거** 적용!

<br>

### 사용자 정보 수정 요구사항 리뷰
- actor: 학생
- 선행조건: 로그인
- 주요 흐름
    - 시스템은 로그인한 사용자 정보(주소, 패스워드) 보여줌
    - 학생은 사용자 정보 수정
        - 이때 시스템은 패스워드가 올바른지 검사 `E-1`

<br>

#### 예외흐름
- E-1
    - 시스템은 패스워드가 4자리 이상이고, 공란이 포함되어 있지 않은지 검사
    - 패스워드가 4자리 이상이거나 공란이 포함되어 있으면 시스템은 수정이 불가능함을 알림

<br>

## 📋 사용자 정보 수정 트리거: BeforeUpdateStudent
---

## BeforeUpdateStudent
- 관련 테이블: student
- 트리거 발생 시기: 수정 전
- 트리거 형태: 행 트리거
    - 행의 실제 값 제어
- 결과
    - 암호의 길이가 4자리 미만인 경우
        - 에러번호 `-20002`, 에러 설명 '암호는 4자리 이상이어야 합니다.' 오류 발생
    - 암호에 공란이 포함된 경우
        - 에러번호  `-20003`, 에러 설명 '암호에 공란은 입력되지 않습니다.' 오류 발생
    - 암호가 정상적인 경우
        - 수정완료

<br>

### trigger.sql

<script src="https://gist.github.com/bokyung124/477e1c8c7f215498721519e12220551e.js"></script>

<br>

### 사용자 정보 수정 후 결과 확인
- BeforeUpdateStudent 트리거 실행 결과 확인
    - 암호 길이 4자리 미만으로 하여 student 수정
        - `ORA-20002: 암호는 4자리 이상이어야 합니다.` 에러 발생
        - student 테이블은 수정되지 않음
    - 암호에 공란이 포함되도록 하여 student 수정
        - `ORA-20003: 암호에 공란은 입력되지 않습니다.` 에러 발생
        - student 테이블은 수정되지 않음

<br>

#### 사용자 정보 수정 후 결과

```sql
UPDATE student 
SET s_pwd = '12'
WHERE s_id = '20011234';

/*

UPDATE student SET s_pwd = '12' WHERE s_id = '20011234';
*
ERROR at line 1:
ORA-20002: 암호는 4자리 이상이어야 합니다.
ORA-06512: at “DB.BEFOREUPDATESTUDENT", line 23
ORA-04088: error during execution of trigger ‘DB.BEFOREUPDATESTUDENT'

*/
```

```sql
UPDATE student
SET s_pwd = '1 345'
WHERE s_id = '20011234';

/*

UPDATE student SET s_pwd = '1 345' WHERE s_id = '20011234';
*
ERROR at line 1:
ORA-20003: 암호에 공란은 입력되지 않습니다.
ORA-06512: at " DB.BEFOREUPDATESTUDENT", line 25
ORA-04088: error during execution of trigger ' DB.BEFOREUPDATESTUDENT'
```