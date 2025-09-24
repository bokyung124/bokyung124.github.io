---
title: "[DBP] CH1-3. Integrity Constraints"
last_modified_at: 2023-04-05T22:04:00-05:00
layout: post
categories:
    - SQL
excerpt: OracleDB) Integrity Constraints
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [lecture, OracleSQL]
---

## 🍏 Integrity Constraints

### 칼럼 레벨 제약 조건
- 칼럼 선언할 때 datatype 옆에 정의
- `NOT NULL` 제약 조건은 칼럼 레벨에서만 정의 가능!
```sql
Column datatype [CONSTRAINT constraint_name] contraint_type
```

<br>

### 테이블 레벨 제약 조건
- `NOT NULL`을 제외한 나머지 제약 조건 정의 가능
```sql
column datatype,
...
[CONSTRAINT constraint_name] PRIMARY KEY (column1 [, column2, ...]);
```

<br>

## 🍏 데이터 무결성 제약 조건

### NOT NULL
- 칼럼 레벨 제약 조건
- 칼럼에서 `NULL`을 허용하지 않도록 함
    - INSERT문에서 `NULL`을 입력하면 에러 발생
- 명시하지 않으면 default로 `NULL` 허용

<br>

```sql
CREATE TABLE book1 (
    title varchar2(100) CONSTRAINT book1_nn NOT NULL,
    author varchar2(100),
    pub_year varchar2(20));
```

<br>

### PRIMARY KEY (기본키)
- 테이블에 대한 기본키 생성
- 테이블 당 **하나의 기본키만** 존재 가능
- 테이블에서 각 행을 유일하게 식별하는 칼럼 또는 칼럼의 집합
    - `UNIQUE`와 `NOT NULL` 제약 조건 동시에 만족!

<br>

```sql
Column datatype [CONSTRAINT constraint_name] PRIMARY KEY (column1 [, column2, ...])

-- or

Column datatype,
...
[CONSTRAINT constraint_name] PRIMARY KEY (column1 [, column2, ...]);
```

<br>

```sql
CREATE TABLE book2 (
    title varchar2(100) CONSTRAINT book1_pk PRIMARY KEY,
    author varchar2(100),
    pub_year varchar2(20));

-- or

CREATE TABLE book2 (
    title varchar2(100),
    author varchar2(100),
    pub_year varchar2(20),
    CONSTRAINT book2_pk PRIMARY KEY(title));
```

<br>

### FOREIGN KEY (외래키)
- 기본키를 참조하는 칼럼 또는 칼럼들의 집합
- 외래키를 가지는 칼럼의 데이터형은 외래키가 참조하는 기본키의 칼럼과 데이터형이 일치해야 함
- 외래키에 의해 참조되고 있는 기본키는 삭제할 수 없음
- `ON DELETE CASCADE` 연산자와 함께 정의된 외래키의 데이터는 그 기본키가 삭제될 때 같이 삭제됨

<br>

```sql
Column datatype [CONSTRAINT constraint_name] FOREIGN KEY (column1 [, column2, ...])

-- or

Column datatype,
...
[CONSTRAINT constraint_name] FOREIGN KEY (column1 [, column2, ...])
REFERENCES table_name(column1 [, column2, ...] [ON DELETE CASCADE]);
```

<br>

```sql
CREATE TABLE review (
    rev_id number(4) CONSTRAINT review_pk PRIMARY KEY,
    rev_title varcharw(100) CONSTRAINT review_fk REFERENCES book1(title),
    rev_con varchar2(500),
    rev_date varchar2(20));

-- or

CREATE TABLE review (
    rev_id number(4) CONSTRAINT review_pk PRIMARY KEY,
    rev_title varcharw(100),
    rev_con varchar2(500),
    rev_date varchar2(20),
    CONSTRAINT review_fk FOREIGN KEY(rev_title) REFERENCES book1(title));
```

<br>


### UNIQUE
- 데이터의 유일성 보장
- 중복되는 데이터가 존재할 수 없음
- 기본키와 유사하나 `NULL` 허용

<br>

```sql
Column datatype [CONSTRAINT constraint_name] UNIQUE

-- or

Column datatype,
...
[CONSTRAINT constraint_name] UNIQUE (column1 [, column2, ...]);
```

<br>

```sql
CREATE TABLE review (
    rev_id number(4) CONSTRAINT review_uk UNIQUE,
    rev_title varcharw(100),
    rev_con varchar2(500),
    rev_date varchar2(20),
    CONSTRAINT review_fk FOREIGN KEY(rev_title)
    REFERENCES book1(title));

-- or

CREATE TABLE review (
    rev_id number(4),
    rev_title varcharw(100),
    rev_con varchar2(500),
    rev_date varchar2(20),
    CONSTRAINT review_uk UNIQUE(rev_id),
    CONSTRAINT review_fk FOREIGN KEY(rev_title)
    REFERENCES book1(title));
```

<br>


### CHECK
- 칼럼의 값을 특정 범위로 제한

<br>

```sql
Column datatype [CONSTRAINT constraint_name] CHECK (condition)

-- or

Column datatype,
...
[CONSTRAINT constraint_name] CHECK (condition);
```

<br>

```sql
CREATE TABLE review (
    rev_id number(4) CONSTRAINT review_ck CHECK(rev_id >= 100 AND rev_id < 500>),
    rev_title varcharw(100),
    rev_con varchar2(500),
    rev_date varchar2(20),
    CONSTRAINT review_uk UNIQUE(rev_id),
    CONSTRAINT review_fk FOREIGN KEY(rev_title)
    REFERENCES book1(title));

-- or

CREATE TABLE review (
    rev_id number(4),
    rev_title varcharw(100),
    rev_con varchar2(500),
    rev_date varchar2(20),
    CONSTRAINT review_uk UNIQUE(rev_id),
    CONSTRAINT rev_ck CHECK (rev_id >= 100 AND rev_id < 500>),
    CONSTRAINT review_fk FOREIGN KEY(rev_title)
    REFERENCES book1(title));
```

<br>

- 정규표현식도 가능
    `CHECK(regexp_like(stu_email, '*.@.*'))`

<br>

## 🍏 제약 조건 변경
- 기존의 테이블에 새로운 제약 조건 추가하기 위해서는 `ADD` 절 이용
```sql
ALTER TABLE table_name
ADD [CONSTRAINT constraint_name] constraint_type(column_name);
```

<br>

## 🍏 제약 조건 삭제
- 기존 테이블에 대한 제약 조건 삭제는 `DROP` 절 이용
```sql
ALTER TABLE table_name
DROP PRIMARY KEY | UNIQUE(column) | 
    CONSTRAINT constraint_name
[CASCADE];
```
- `CASCADE` 옵션은 삭제하려는 제약 조건을 참조하는 모든 제약 조건들도 같이 삭제됨

<br>

## 🍏 제약 조건 확인
- Data Dictionary
    - 데이터베이스에 저장되는 데이터에 대한 정보(메타데이터)를 저장해놓은 테이블
    - **sys.user_constraints** 테이블
    - **sys.user_cons_columns** 테이블
    - 속성, NOT NULL 여부, 유형

<br>

```sql
desc user_constraints;
```

![IMG_25B47E8757F6-1](https://user-images.githubusercontent.com/53086873/230131460-c9f95d45-17a6-4161-a014-7aeb4abc4dc1.jpeg)   

<br>

### sys.user_constraints

|컬럼|의미|
|---|---|
|owner|제약 조건을 소유하는 사용자|
|constraint_name| 제약 조건 이름|
|constraint_type|제약 조건 유형 (U, C, P, R)|
|table_name|제약 조건이 속한 테이블|
|search_condition|constraint_type이 C `NOT NULL / CHECK` 인 행에 대해 각각의 조건 나타냄|
|r_constraint_name|제약 조건이 FK인 경우 이것이 참조하는 PK 표시|

<br>

### sys.user_cons_columns
- 어떤 칼럼에 어떤 제약 조건들이 정의되어 있는지 보여주는 데이터 사전

<br>

```sql
desc user_cons_columns;
```

![IMG_645E958BADB3-1](https://user-images.githubusercontent.com/53086873/230132896-4fc6f843-6ab3-4da9-aa99-537b60813f55.jpeg)

<br>

## 🍏 제약 조건 DISABLE / ENABLE
- 제약 조건을 삭제하지 않고 적용시키거나 적용되지 않도록 하는 방법
- `DISABLE` : 적용 X
- `ENABLE` : 다시 적용 (조건에 맞는 데이터만 있어야 다시 ENABLE 가능)
- `DISABLE` 후 `ENABLE` 실행 전까지는 로그아웃 후 다시 로그인

<br>

```sql
ALTER TABLE table_name
DISABLE CONSTRAINT constraint_name;

ALTER TABLE table_name
ENABLE CONSTRAINT constraint_name;
```