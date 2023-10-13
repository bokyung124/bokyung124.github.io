---
title: "[pilot] Ch2. 파일럿 프로젝트 아키텍처 설계(2)"
last_modified_at: 2023-09-22T14:46:00-05:00
layout: post
categories:
    - Hadoop
excerpt: 
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [study, Hadoop, 파일럿프로젝트]
---

[출처: 실무로 배우는 빅데이터 기술, 김강원 저]

## 1. 클라우데라 매니저(CM) 설치

- CM : 빅데이터 에코시스템을 쉽게 설치하고 관리해주는 빅데이터 시스템 자동화 도구
- 빅데이터 소프트웨어에 대한 프로비저닝, 매니지먼트, 모니터링 수행
  - 프로비저닝 : 하둡 에코시스템 편리하게 설치, 삭제, 수정 관리
  - 매니지먼트 : 설치한 에코시스템의 설정 변경 및 최적화 지원
  - 모니터링 : 하드웨어의 리소스 및 설치 컴포넌트의 상태 모니터링 / 대시보드

<br>

## 2. 가상머신 서버 설치

- 원래는 명령어를 이용하여 CM을 설치해야 하지만, 현재 CM 정책이 수정되어 책에 나와있는 명령어로 설치가 안됨
- 저자님의 깃허브에서 가상머신 2개 이미지 파일을 받을 수 있음

https://drive.google.com/file/d/1oLikMIC6bzt0jNV0n49YNOM0foNPXDZh/view?usp=sharing 

<br>

- 기존에 설치했던 서버들을 지우고, 이 이미지 파일로 서버를 설치하면 됨

<br>

## 3. 파일럿 pc 운영체제 호스트 파일 수정

- 메모장 관리자 권한으로 실행
- [파일] - [열기] 에서 C:\Windows\System32\drivers\etc 로 이동 후 hosts 파일 열기
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FAAk4M%2FbtrVOztPphs%2FukJmfqv1cQbcxb0ehpKQT0%2Fimg.png)

- 가상머신에 설치한 리눅스 서버의 IP/도메인명 정보 입력 후 저장 (server01, server02만 입력)

<br>

## 4. 크롬으로 CM 접속

[](http://server01.hadoop.com:7180)

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FoAePZ%2FbtrVQN5VGHq%2FL05FOfb1W8eRNb8GA3wuj0%2Fimg.png)

- 기동하는데 시간이 조금 걸리기 때문에 접속이 바로 안되더라도 여러 번 새로고침
- 사용자 이름, 암호 모두 admin  

<br>

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbGNmVJ%2FbtrVT73Coaa%2FYnPz6ZgiGsQ7C2dOwv0yj1%2Fimg.png)
- CM 첫화면
- 우선은 HDFS, YARN, ZooKeeper 만 설치  

<br>

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbiV0mK%2FbtrVUAK303T%2Fxxbj3ECFODv21OU24TFd61%2Fimg.png)
- CM 홈화면
- 각 서버의 리소스(CPU,  메모리, 디스크, I/O 등)와 설치된 SW 모니터링하며 현재 상태값 보여줌
- 각 소프트웨어가 불량으로 표시되어도, 정지 상태가 아니라면 진행에 문제 없음 -> 리소스 절약   

<br>

## 5. HDFS 구성 변경

### 1) HDFS 복제 계수 설정
- 하둡에서 원본 파일을 저장하면 안정성을 위해 2개의 복제본 추가로 생성해 총 3개의 파일 만들어짐
- 파일럿 프로젝트에서는 2개로도 충분하기 때문에 2개로 변경
- 복제 계수를 늘리면 여러 데이터노드에 파일이 분산 저장되어 분석 작업시 성능 극대화 

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FlO3FO%2FbtrVRCwsHuf%2FhovRKbctGPWa5QcvzHUVz0%2Fimg.png)

<br>

### 2) HDFS 접근 권한 해제
- 하둡 파일시스템에 대한 접근 권한 해제
- 테스트 환경을 고려한 설정. 실제 플젝에서는 계정별로 접근 권한 분리하여 적용
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcCb6vH%2FbtrVRDvmBcz%2F4AQhAt2qGnLGnALYknfuyK%2Fimg.png)   

<br>

## 3) HDFS 블록 크기 변경
- 128MB -> __64MB__
- 파일럿 프로젝트에서 수집/적재하는 파일의 최대 크기는 110MB
- 하둡은 기본 블록 크기보다 작은 파일 처리시 효율성 떨어짐
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2F0C4zG%2FbtrVUzSZKIw%2Fht8VbB1dOjxiisgA2Whpx0%2Fimg.png)   

<br>

## 6. YARN 구성 변경

- YARN 스케줄러와 리소스매니저 메모리 크기 설정
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fb5XatB%2FbtrVTUKvbhZ%2F4CyGaZuuIF4YhlBQIlrzW1%2Fimg.png)
- 1 -> __1.5 GiB__

<br>

### 2) YARN 스케줄러 변경
- 하둡에서 job이 실행될 때 YARN의 스케줄러가 분산 데이터노드의 리소스를 고려해 잡 스케줄링
- FairScheduler -> __FIFOScheduler__
- Fair가 더 개선된 스케줄이지만, 개인의 pc로 이용하기에는 리소스 경합이 발생해 병목 현상 발생
> 병목 현상 : 두 구성 요소의 최대 성능의 차이로 인해 한 구성 요소가 다른 하드웨어의 잠재 성능을 제한하는 것

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcQSRkk%2FbtrVUmfmWGe%2Fj1RBAu5WxDgHe3RDrYkjm0%2Fimg.png)   

<br>

## 7. 클러스터 재시작

- 설정들 최종 반영하기 위해 클러스터 재시작
- 홈에서 [Cluster 1] - [작업] - [재시작]
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcQEJbM%2FbtrVT8oaLnU%2F7Dq2jSHGK5S9GSxY4zG58K%2Fimg.png)   
<br>

## 8. HDFS 예제 실습

- 저자님 깃허브에서 예제소스 폴더 다운로드 (제가 올려도 되는건지 모르겠어서 링크는 생략하겠습니다)

## 1) Filezilla로 샘플 txt 파일 -> server02 /home/bigdata 로 전송
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2F7U9Wk%2FbtrVRDWCHvw%2F1LtsmVSqFnZmyaqunxumN1%2Fimg.png)   
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FswFYF%2FbtrVUiYoJlt%2FWWsNvYz7QRfLkS5exLtJd0%2Fimg.png)    

<br> 

> HDFS 명령어   
https://hadoop.apache.org/docs/r3.1.2/hadoop-project-dist/hadoop-common/FileSystemShell.html

<br>

```bash
hdfs dfs [GENERIC_OPTIONS] [COMMAND_OPTIONS]
```
```bash
# cat : 파일 읽어서 보여줌 (리눅스 cat과 동일)
hdfs dfs -cat [경로]

# count : 폴더, 파일, 파일 사이즈
hdfs dfs -count [경로]

# ls : 디렉터리 내부 파일
hdfs dfs -ls [디렉터리]

# mkdir : 특정 path에 디렉터리 생성
hdfs dfs -mkdir (-p) [path]

# cp : 파일 복사
hdfs dfs -cp [소스 경로] [복사 경로]
```

<br>

### 2) 파일 저장 및 확인
```bash
cd /home/bigdata
hdfs dfs -put Sample.txt /tmp
```
- Sample.txt 파일이 HDFS의 /tmp 디렉터리로 저장됨

<br> 

```bash
hdfs dfs -ls /tmp
```
- 파일 목록에 Sample.txt 존재

<br>

### 3) 파일 내용 보기
```bash
hdfs dfs -cat /tmp/Sample.txt
```
<br>

### 4) 저장한 파일 상태 확인
```bash
hdfs dfs -stat '%b %o %r %u %n' /tmp/Sample.txt
```
- 파일 크기, 파일 블록 크기, 복제 수, 소유자명, 파일명 정보 보여줌

<br>

### 5) 파일 이름 바꾸기
```bash
hdfs dfs -mv /tmp/Sample.txt /tmp/Sample2.txt
```
- Sample.txt -> __Sample2.txt__ 로 변경

<br>

### 6) 파일 시스템 상태 검사
```bash
hdfs fsck /
```
- 전체 크기, 디렉터리 수, 파일 수, 노트 수 등 파일 시스템의 전체 상태 보여줌

<br>

```bash
hdfs dfsadmin -report
```
- 하둡 파일시스템의 기본 정보 및 통계 보여줌

<br>

* HDFS 파일의 비정상 상태
    - HDFS 점검 명령을 실행할 때 파일 시스템에 문제가 발생할 경우 "CORRUPT FILES", "MISSING BLOCKS", "MISSING SIZE", "CORRUPT BLOCKS" 등의 항목에 숫자가 표기됨
    - 이 같은 상태가 지속되면 하둡은 물론 HBase, 하이브 등에 부분적인 문제 발생 가능
    - HDFS는 비정상적인 파일 블록 발견한 경우 다른 노드에 복구하려고 시도, 사용자가 직접 삭제/이동 명령 조치할 수 있음


```bash
# 강제로 안전모드 해제
hdfs dfsadmin -safemode leave

# 손상된 파일 강제로 삭제
hdfs fsck / -delete

# 손상된 파일을 /lost + found 디렉터리로 이동
hdfs fsck / -move
```

<br>

## 9. 주키퍼 클라이언트 명령을 이용한 설치 확인

### 1) zookeeper-client 실행
```bash
zookeeper-client
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fb1RBT0%2FbtrWzRkXLZN%2FjQqdo6KAYMCJBPd38wNgOK%2Fimg.png)   
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FFYtuR%2FbtrWw73p7Oj%2F57nMmLAg60caCRCEGR1nMK%2Fimg.png)   

<br>

### 2) 주키퍼 z노드 등록/조회/삭제

```bash
create /pilot-pjt bigdata
ls /
get /pilot-pjt
delete /pilot-pjt
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcjgD2u%2FbtrWxquRFRa%2F8ZblaH486UKM7KSZhepIE0%2Fimg.png)   

- bigdata를 담고 있는 pilot-pjt 라는 znode 생성, 조회, 삭제

<br>


* zookeeper와 znode
    - zookeeper : 분산 어플리케이션을 구성하기 쉽게 도와주는 시스템 (znode로 구성된 분산 데이터 모델을 지원하는 시스템)
    - z노드 : 클러스터를 구성하고 있는 각각의 서버
    - 주키퍼는 데이터를 디렉터리 구조로 관리하며, key-value 스토리지처럼 key로 접근 가능
    - 디렉터리 구조의 각 데이터 노드가 znode


> 참고 사이트     
https://engkimbs.tistory.com/660

<br>

## 10. 스마트카 로그 시뮬레이터 설치

### 1) server02에 작업 폴더 생성
```bash
cd /home
mkdir -p /home/pilot-pjt/working/car-batch-log
mkdir /home/pilot-pjt/working/driver-realtime-log
chmod 777 -R /home/pilot-pjt
```

<br>

### 2) 자바 컴파일, 실행 환경 변경 (1.7 -> 1.8)
```bash
rm /usr/bin/java
rm /usr/bin/javac
ln -s /usr/java/jdk1.8.0_181-cloudera/bin/javac /usr/bin/javac
ln -s /usr/java/jdk1.8.0_181-cloudera/bin/java /usr/bin/java
```

```bash
java -version
``` 
- 1.8.0_181 확인   

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FDuWeE%2FbtrWv8B0NEs%2FjCK9ED53KM8zf0y46hF8G0%2Fimg.png)

<br>

### 3) 자바로 만들어진 스마트카 로그 시뮬레이터 프로그램 server02에 업로드
- 파일질라 이용
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FceNJHe%2FbtrWxtrCjBC%2FkF7u4u2kDS90Gnx38nQYK1%2Fimg.png)   

- bigdata.smartcar.loggen-1.0.jar 파일을 /home/pilot-pjt/working에 업로드

<br>

### 4) 스마트카 로그 시뮬레이터 실행
- `bigdata.smartcar.loggen-1.0.jar` 파일에 두 개의 메인 자바프로그램이 있음
    - 스마트카 운전자의 운행 정보를 실시간으로 발생시키는 `DriverLogMain.java`
    - 스마트카의 상태 정보를 주기적으로 발생시키는 `CarLoginMain.java`

<br>

- `DriverLogMain.java` 먼저 실행
```bash
cd /home/pilot-pjt/working
java -cp bigdata.smartcar.loggen-1.0.jar com.wikibook.bigdata.smartcar.loggen.DriverLogMain 20160101 10
```


* java -cp [경로] [클래스 이름]  (현재 열려 있는 명령 창에서만 유효)
    - cp (classpath) : JVM이 프로그램을 실행할 때 클래스 파일을 찾는 데 기준이 되는 파일 경로, JVM의 매개 변수
    - 자바에서 외부 라이브러리 파일이나 jar 파일 포함하여 컴파일하기 위해서는 classpath 이용


- __bigdata.smartcar.loggen-1.0.jar__ : 포함하고자 하는 라이브러리나 jar 파일 (필요한 클래스 파일들)
- __com.wikibook.bigdata.smartcar.loggen.DriverLogMain__ : 컴파일 할 파일

<br>

- __시뮬레이터 작동 확인__
```bash
cd /home/pilot-pjt/working/driver-realtime-log
tail -f SmartCarDriverInfo.log
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2F0Y5EV%2FbtrWzRZA0Hx%2FR9Jloh0FrZuJ8vSS2TO9L0%2Fimg.png)   

<br>

- __데이터 형식 정의__   

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbiqEGG%2FbtrWx8Hv5jU%2FWCKW0a6yZ6GUqpKRrZKitK%2Fimg.png)

<br>

- __CarLogMain.java 실행__
```bash
cd /home/pilot-pjt/working
java -cp bigdata.smartcar.loggen-1.0.jar com.wikibook.bigdata.smartcar.loggen.CarLogMain 20160101 10
```


* 코드 설명
    - 첫번째 매개 변수: 실행 날짜 
    - 두번째 매개 변수: 스마트카 대 수
    -> 2016년 1월 1일 기준으로 10대의 스마트카에 대한 로그 파일인 SmartCarStatusInfo_20160101.txt 생성됨


<br>

- __시뮬레이터 작동 확인__
```bash
cd /home/pilot-pjt/working/SmartCar
tail -f SmartCarStatusInfo_20160101.txt
```
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fef6z6h%2FbtrWwgGOUHT%2FD1z6WrbOshWUdPvkjEiYCk%2Fimg.png)   

<br>

- __데이터 형식 정의__   

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fbu0fNq%2FbtrWx5c0MEM%2FU9JS4am5kifZ5iqA58Bk50%2Fimg.png)