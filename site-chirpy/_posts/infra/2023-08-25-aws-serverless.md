---
title: "[AWS] AWS Serverless"
last_modified_at: 2023-08-25T16:47:00-05:00
layout: post
categories:
    - Infra
excerpt: aws serverless
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [study, AWS]
---

## 1. Network Topology

- 컴퓨터의 네트워크 요소들 (링크, 노드 등)을 물리적으로 연결해 놓은 것, 또는 그 연결 방식

<br>

## 2. Client - Server

- Client
    - 네트워크의 말단에서
    - 자원 요청
    - 서비스를 활용하는

- Server
    - 네트워크의 중앙에서 
    - 자원 공유
    - 데이터 처리 및 저장

<img width="334" alt="스크린샷 2023-08-25 오후 5 42 09" src="https://github.com/bokyung124/infra-study/assets/53086873/ddd1a133-f7bb-4b8d-ac0d-735a9d522b6a">

<br>

## 3. WAS

- Web Application Server

<img width="534" alt="스크린샷 2023-08-25 오후 5 42 41" src="https://github.com/bokyung124/infra-study/assets/53086873/917b6763-a6dc-4a92-9d5d-f698b963305a">

- DB 조회나 다양한 로직 처리를 요구하는 동적인 컨텐츠를 제공하기 위해 만들어진 Application Server
- HTTP를 통해 컴퓨터나 장치에 애플리케이션을 수행해주는 미들웨어
- Web Server 기능들을 구조적으로 분리하여 처리하고자 하는 목적으로 제시됨
    - 분산 트랜잭션, 보안, 메시징, 쓰레드 처리 등의 기능을 처리하는 분산 환경에서 사용됨
    - 주로 DB 서버와 같이 수행됨

- 주요 기능
    - 프로그램 실행 환경과 DB 접속 기능 제공
    - 여러 개의 트랜잭션 관리 기능
    - 업무를 처리하는 비즈니스 로직 수행

- ex
    - Tomcat, JBoss, Jeus, Web Sphere 등

- Web Server
    - 웹 브라우저 클라이언트로부터 HTTP 요청을 받아 정적인 컨텐츠를 제공하는 프로그램
    - ex) Apache Server, Nginx, IIS 등

<br>

## 4. Serverless

- 코드 실행, 데이터 관리 및 애플리케이션 통합을 위한 기술을 **서버를 관리할 필요 없이** 제공
- 서버가 없는 것이 아니라, 서버를 운영하고 관리할 필요가 없는 것!

- ex) 애플리케이션에서 특정 function만 만들고 싶은 경우
    - 카카오톡에서 특정 단어가 나오면 알람이 뜨도록
    - 원래는 따로 앱을 만들고, aws 서버를 이용해야 했음

- 백엔드(Baas)와 서비스로서의 기능(Faas)

- ex
    - AWS Lambda
    - Azure Functions
    - IBM Cloud Functions

<br>

## 5. Lambda

- 파일 처리
<img width="442" alt="스크린샷 2023-08-25 오후 5 48 56" src="https://github.com/bokyung124/infra-study/assets/53086873/c7c28109-a180-4aa3-a188-db7570f40139">

- 스트림 처리
<img width="451" alt="스크린샷 2023-08-25 오후 5 49 22" src="https://github.com/bokyung124/infra-study/assets/53086873/d20af33d-cb65-47f0-9b1e-b297bc1bc87d">

- 웹 어플리케이션
<img width="453" alt="스크린샷 2023-08-25 오후 5 49 47" src="https://github.com/bokyung124/infra-study/assets/53086873/d844606a-703d-4dfb-a646-7fb422ba6d1c">

- 모바일 백엔드
<img width="452" alt="스크린샷 2023-08-25 오후 5 50 05" src="https://github.com/bokyung124/infra-study/assets/53086873/cf2f82a6-cb72-49e6-a396-803ad71ce1f1">


<br>

### case 1) Coca-Cola

- AWS Lambda를 이용하여 실시간으로 non-contact 음료 서비스 제공
- QR 코드를 카메라에 인식하면 사용자의 인터페이스에 앱이 아닌 Coca-Cola Freestyle 인터페이스를 모바일 디스플레이에 띄워줌

<br>

### case 2) 타다

- AWS Lambda를 사용하여 드라이버의 pdf 정보 파일을 분류하는 기능 구현
- 드라이버의 인증과 면허 등록 등 업로드 받은 pdf 파일을 분류, 저장하는 기술
- 이를 Lambda에서 python 라이브러리를 통해 간단하게 구현함

<br>

- 두 케이스 모두 보안이 의문!

<br>

## 6. Fargate

<img width="593" alt="스크린샷 2023-08-25 오후 5 52 45" src="https://github.com/bokyung124/infra-study/assets/53086873/e8e497a0-57bc-471f-870a-1fed3892fdd9">

- 안전한 마이크로서비스 구축
- 아이디어에서 출시까지 걸리는 시간 단축
- 요구사항에 적합한 컴퓨팅 및 컨테이너 오케스트레이터 선택
- 높은 안정성으로 AWS 전체의 통합 지원

<br>

### Fargate vs. Lambda

<img width="625" alt="스크린샷 2023-08-25 오후 6 00 31" src="https://github.com/bokyung124/infra-study/assets/53086873/27663fe4-4828-4221-96c6-38811138c7b6">

- Fargate는 EC2 머신을 AWS에서 직접 업데이트 및 관리를 해주는 차이점

- Fargate
    - 특성상 1 Node에 1 Pod만 가능해서 구조상 Daemonset이 뜰 수 없으며, AWS 쪽에서 직접 운영하기 때문에 권한이 제한되어 있음
    - 하지만 Fargate를 이용하면 인프라 관리자들의 관리포인트가 줄어들고, 1 Node에 1 Pod 구조만 가능하여 같은 Node에 떠 있는 특정 Pod의 영향으로 인한 성능 저하를 일으킬 수 있는 이슈가 없고, 머신 성능을 풀로 사용할수 있어서 상황에 맞게 사용하면 좋음

- 참고 링크    
https://jflip.tistory.com/41

<br>

### case 1) Vanguard

- 금융 회사
- IT 부서의 업무 부담을 줄이고, 새로운 서비스를 실험하는 데 인력을 집중
- DevOps를 다이나믹하게 운영

<br>

### case 2) SAMSUNG

- 자사 서버가 없는 대규모 IT 서비스 기업
- IT를 표방하지만 기반은 제조업인 독특한 구조의 글로벌 기업
- 다분야의 팀으로 구성된 기업 환경에 맞게 팀 단위의 Fargate 구성

<img width="572" alt="스크린샷 2023-08-25 오후 6 04 48" src="https://github.com/bokyung124/infra-study/assets/53086873/35820623-3c9d-4f31-84fc-253bb2f46a35">