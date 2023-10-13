---
title: "[MySQL] SQL 옵티마이저"
last_modified_at: 2023-06-24T22:24:00-05:00
layout: post
categories:
    - SQL
excerpt: MySQL) Optimizer
toc: true
toc_sticky: true
author_profile: true
mathjax: true
tag: [MySQL]
---

![image](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fm94Oz%2FbtqTNBsMZ9x%2FHkuOTKjJ2Kv94M0wz8BtM0%2Fimg.png)

SQL 실행 과정

<br>

## 1. SQL 파싱 (PARSING)

SQL 파싱은

1) SQL 문장에 **문법적 오류**가 없는지 검사 (Syntax 검사)    
2) **의미상 오류**가 없는지 검사 (Semantic 검사)    
3) 사용자가 발생한 SQL과 그 실행계획시 **라이브러리캐시(프로시저캐시)에 캐싱되어 있는지** 확인    
4) 캐싱되어 있다면 **소프트파싱**, 캐싱되어있지 않다면 **하드파싱**    

으로 구성된다.

<br>

> 소프트파싱: SQL과 실행계획을 캐시에서 찾아 곧바로 실행단계로 넘어가는 경우   
> 하드파싱: SQL과 실행계획을 캐시에서 찾지 못해 최적화 과정을 거치고나서 실행단계로 넘어가는 경우   

> 라이브러리캐시는 해시구조로 엔진에서 관리된다. SQL마다 해시값에 따라 여러 해시 버킷으로 나뉘며 저장되고, SQL을 찾을 때는 SQL 문장을 해시 함수에 적용하여 반환되는 해시값을 이용해서 해시 버킷을 탐색한다.

<br>

## 2. 규칙기반 옵티마이저 (RBO)

실행계획을 정해진 룰에 따라 만든다.    
룰은 데이터베이스 엔진마다 여러 가지가 있다.    

예를 들어서 오라클의 RBO는 다음과 같다.     

|순위|액세스 경로|
|---|---|
|1|Single Row by Rowid|
|2|Single Row by Cluster Join|
|3|Single Row by Hash Cluster Key with Unique or Primary Key|
|4|Single Row by Unique or Primary Key|
|5|Clustered Join|
|6|Hash Cluster Key|
|7|Indexed Cluster Key|
|8|Composite Index|
|9|Single-Column Indexes|
|10|Bounded Range Search on Indexed Columns|
|11|Unbounded Range Search on Indexed Columns|
|12|Sort Merge Join|
|13|MAX or MIN of Indexed Column|
|14|ORDER BY on Indexed Column|
|15|Full Table Scan|

자세한 과정은 잘 모르겠지만, 크게 보면 엑세스를 할 때에 인덱스를 이용하느냐, 전체 테이블을 스캔하느냐 등으로 나눌 수 있다. 1번부터 순서대로 맞는 경우에 진행하며, 아래로 갈수록 data가 흐트러져서 저장되기 때문에 비용이 많이 든다.     
그리고 요즘에는 대부분 RBO보다 CBO를 이용한다.

<br>

## 3. 비용기반 옵티마이저 (CBO)

비용을 기반으로 최적화를 수행하는 방식이다. 이때 비용이란 쿼리를 수행하는데 소요되는 일의 양 또는 시간 예상치이다.   

![image](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2F9DJ6V%2FbtqTPxKrhJW%2FaH5NoMZxKZqUmKBKTq8X40%2Fimg.png)

딕셔너리에서 테이블과 인덱스를 통해 레코드 개수, 블록 개수, 평균 행 길이, 칼럼 값의 수, 칼럼 값 분포, 인덱스 높이, 클러스터링 팩터 등의 통계값을 기반으로 비용을 예측하는 방식이다.    
이 예측된 비용에 따라 최적의 실행 계획을 도출한다.     
최근에는 추가적으로 하드웨어적 특성을 반영한 시스템 통계정보 (CPU 속도, 디스크 I/O 속도 등)까지 이용한다.

<br>

## 4. SQL 실행계획

실행 계획은 SQL에서 요구한 사항을 처리하기 위한 절차와 방법을 의미한다. 즉, SQL을 어떤 순서로 어떻게 진행할 지 결정한다는 것이다.

실행 계획의 구성요소는 다음 다섯 가지가 있다.

- **조인 순서 (Join Order)** : JOIN 수행에서 어떤 테이블이 먼저 조회되는가
- **조인 기법 (Join Method)** : loop, merge, sorting 등
- **액세스 기법 (Access Method)** : Index / Full table 등
- **최적화 정보 (Optimization Information)** : 알고리즘
- **연산 (Operation)** : 크다, 작다, 함수, MAX, MIN 등


![image](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fbh8nE1%2FbtqTJlLfEkR%2F3l0j9puo2LQl9JvSGUlYg1%2Fimg.png)

<br>

## 5. INDEX

INDEX는 데이터베이스 분야에 있어서 테이블에 대한 동작의 속도를 높여주는 자료 구조이다.

```sql
CREATE INDEX IDX_### ON db, table (column);
ALTER TABLE db.table ADD INDEX IDX_###;
```

두 코드 모두 column에 대한 INDEX를 생성하는 코드이다.

<br>

```sql
ALTER TABLE db.table DROP INDEX IDX_###;
```

테이블에 있는 인덱스를 삭제하는 코드이다.

<br>

```sql
EXPLAIN SELECT * FROM db.table;
```

실행 계획을 확인하는 코드이다.

<br>

### 예제) 

```sql
DESC kaggle.titanic;
```

![image](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FztOUG%2FbtqTIpNTltA%2FXCdVBuryjbNcVqW14hYr31%2Fimg.png)

```sql
EXPLAIN SELECT * FROM kaggle.titanic WHERE `Age` = 23;
```

![image](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbpWY0Y%2FbtqTJTOvjTu%2FPBDVHZw24vbLj7k41kYeXK%2Fimg.png)

> Age가 23인 데이터를 찾기 위해 418개의 rows를 모두 검색하는 것이 플랜임을 알 수 있다.

<br>

#### INDEX 생성 후

```sql
DESC kaggle.titanic;
```

![image](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FkUFeb%2FbtqTYRH4XIT%2F7RMbV1JZebylOsyqoGs4PK%2Fimg.png)

> Age에 인덱스가 생성된 것을 확인할 수 있다.

```sql
EXPLAIN SELECT * FROM kaggle.titanic WHERE `Age` = 23;
```

![image](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fc8UAoG%2FbtqTNzuXuCI%2FMWPmcZGR8JCTZYz0BDjf2k%2Fimg.png)

> IDX_AGE를 사용해서 reference를 통해서 쿼리를 실행하는 것이 플랜임을 알 수 있다.
> 데이터를 얻기 위해서 11개의 row만 검색하면 된다.