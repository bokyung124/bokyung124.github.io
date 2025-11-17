---
title: "[Study] AWS Load Balancing"
last_modified_at: 2023-08-25T16:46:00-05:00
layout: post
categories:
    - AWS
excerpt: aws load balancing
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [study, AWS]
---

## 1. Load Balancing

<img width="668" alt="스크린샷 2023-08-24 오후 6 13 07" src="https://github.com/bokyung124/infra-study/assets/53086873/a64178b0-e4a7-4ad7-ab6b-729cb12aa92e">

- 서버들에게 트래픽을 골고루 분배하는 것

- 목적
    - 트래픽을 여러 서버에 분산 -> 더 많은 리소스를 사용할 수 있도록
    - 각각의 인스턴스에게 트래픽 -> 로드 밸런서만 액세스 포인터를 갖고 있으면 됨
    - 인스턴스에 대한 정기적인 상태 점검 수행
    - 다운스트림 인스턴스의 장애 원활하게 처리

<img width="590" alt="스크린샷 2023-08-24 오후 6 15 31" src="https://github.com/bokyung124/infra-study/assets/53086873/52cf476b-073c-4a56-963c-63e32388d24a">

<br>

## 2. Types of Load Balancer on AWS

- CLB (Classic Load Balancer)
    - HTTP, HTTPS, TCP, SSL (secure TCP)
    - 현재는 EC2 Classic에서를 제외하고 사용하지 않음

- ALB (Application Load Balancer)
    - HTTP, HTTPS, WebSocket

- NLB (Network Load Balancer)
    - TCP, TLS (secure TCP), UDP

- GWLB (Gateway Load Balancer)
    - Operates at layer 3 (Network lyaer) - IP Protocol

<br>

## 3. ALB

<img width="721" alt="스크린샷 2023-08-24 오후 6 18 18" src="https://github.com/bokyung124/infra-study/assets/53086873/4b20d728-1b1c-4aa1-9cc6-e912b2c447e3">

### Target Groups

- EC2 instances / ECS tsks / IP Addresses
- 여러 타겟 그룹으로 라우팅 가능
- 타겟 그룹 레벨에서 health check

<img width="544" alt="image" src="https://github.com/bokyung124/infra-study/assets/53086873/21fc3f3b-a12a-4874-b868-19aadbdb49eb">

- OSI 7계층 중 애플리케이션 계층 (layer 7)에서 동작하는 로드밸런서
- HTTP / HTTPS 프로토콜을 사용하는 트래픽에 대해 로드밸런싱 수행
- 마이크로서비스 / 컨테이너 기반 애플리케이션 구조에 적합

<br>

### Routing Algorithms

<img width="631" alt="스크린샷 2023-08-24 오후 6 20 36" src="https://github.com/bokyung124/infra-study/assets/53086873/72a56c72-cb8c-413f-829f-9eaa53f83866">


- Round-Robin
    - 일정 시간마다 라우팅을 변경하는 알고리즘
    - 기본적인 라우팅 알고리즘

- LOR (Least Outstanding Requests)
    - 처리하고 있는 요청이 가장 적은 인스턴스에게 라우팅

<br>

### ALB vs. CLB

<img width="475" alt="스크린샷 2023-08-24 오후 6 39 32" src="https://github.com/bokyung124/infra-study/assets/53086873/baa6ba46-d05d-4731-ab32-cfa743f7ac41">

<br>

## 4. NLB

<img width="546" alt="스크린샷 2023-08-24 오후 6 47 16" src="https://github.com/bokyung124/infra-study/assets/53086873/80eaf9fd-fc0a-4e48-af81-c64367f0bbe9">

- OSI 7계층 중 전송 계층 (layer 4)에서 동작하는 로드 밸런서
- 초 당 수백만 건의 요청 처리 가능
- 짧은 대기 시간 (~ 100ms)
    - ALB: 400ms
- 최고의 성능이 필요한 TCP / UDP 트래픽에 사용
    - TCP 트래픽
        - 프로토콜, 원본 IP 주소, 원본 포트, 대상 IP 주소, 대상 포트, TCP 시퀀스 번호에 따라 **흐름 해시 알고리즘**을 사용하여 대상 선택
        - 각 TCP 연결은 연결 수명 동안 하나의 대상에 라우팅 됨
    - UDP 트래픽
        - 프로토콜, 원본 IP 주소, 원본 포트, 대상 IP 주소, 대상 포트에 따라 **흐름 해시 알고리즘**을 사용하여 대상 선택
        - UDP 흐름은 TCP와 달리 소스와 목적지가 동일 -> 수명이 다할 떄까지 일관되게 단일 대상으로 라우팅 됨
        - 서로 다른 UDP 흐름에는 서로 다른 소스 IP 주소와 포트가 있으므로 다른 대상으로 라우팅될 수 있음

<br>

## 5. GWLB

<img width="232" alt="스크린샷 2023-08-24 오후 6 47 40" src="https://github.com/bokyung124/infra-study/assets/53086873/be758bc6-4593-4f47-a8f2-9eae91c54168">

- OSI 7계층 중 네트워크 계층 (layer 3)에서 동작하는 로드 밸런서
- 투명한 네트워크 게이트웨이 제공 -> 원본 패킷의 데이터가 중요한 가상 어플라이언스 지원을 위해 개발됨
- AWS에서 타사 네트워크 가상 어플라이언스 구축, 확장 및 관리
- ex) 방화벽, 침입 탐지 및 방지 시스템, 심층 패킷 검사 시스템

- VPC의 라우팅 테이블을 조정해서 GWLB로 트래픽을 보낼 수 있음
- 양방향의 트래픽을 동일한 어플라이언스로 보냄으로써 어플라이언스가 stateful한 트래픽 처리를 수행하도록 함

<br>

## 6. Auto Scaling

- 늘어난 부하에 맞게 scale out (EC2 인스턴스 추가)
- 감소된 부하게 맞게 scale in  (EC2 인스턴스 제거)
- 최소 및 최대 수의 활동 중인 EC2 인스턴스 확보
- 로드밸런서에 새로운 인스턴스 자동 등록
- 이전 인스턴스가 종료되는 경우 EC2 인스턴스 재생성 

### Auto Scaling Group in AWS

<img width="635" alt="스크린샷 2023-08-25 오후 4 44 13" src="https://github.com/bokyung124/infra-study/assets/53086873/9a8fbdd1-21e5-4ea0-978a-de0ce48fbd2d">

### Auto Scaling Group in AWS with load balancer

<img width="610" alt="스크린샷 2023-08-25 오후 4 46 05" src="https://github.com/bokyung124/infra-study/assets/53086873/c7637d50-2dec-47ab-a1fa-bf1c9484e3d7">

<br>

## 7. Auto Scaling Groups

### 1) Dynamic scaling policies

- 대상 추적 스케일링
    - ex) 평균 ASG CPU 약 40% 유지

- 단순 / 단계 스케일링
    - ex) 평균 ASG CPU가 70%를 넘으면 유닛 2개 추가
    -     평균 ASG CPU가 30% 미만이면 유닛 1개 제거

- 예약된 작업
    - 알고 있는 사용 패턴들 기반으로 스케일링 예상
    - ex) 금요일 오후 5시에 최소 용량 10대로 확장

<br>

### 2) Predictive scaling

- 지속적으로 부하를 예측하고 미리 확장 일정 예약

<img width="671" alt="스크린샷 2023-08-25 오후 4 58 05" src="https://github.com/bokyung124/infra-study/assets/53086873/82ea1f5b-d473-42bf-8e12-672682b39ba6">

<br>

## 8. Docker containers management on AWS

- Amazon Elastic Container Service (Amazon ECS)
    - 아마존 자체 컨테이너 플랫폼

- Amazon Elastic Kubernetes Service (Amazon EKS)
    - 아마존의 관리형 쿠버네티스 (오픈소스)

- AWS Fargate
    - 아마존 자체 서버리스 컨테이너 플랫폼
    - ECS, EKS와 함께 사용됨

- Amazon ECR
    - 컨테이너 이미지 저장소

<br>

### 1) Amazon ECS - EC2 launch type

- 인프라 (EC2 인스턴스)를 프로비저닝하고 유지해야 함
- 프로비저닝: 사용자의 요구에 맞게 시스템 자원을 할당, 배치, 배포해 두었다가 필요 시 시스템을 즉시 사용할 수 있는 상태로 미리 준비해 두는 것

<img width="284" alt="스크린샷 2023-08-25 오후 5 04 33" src="https://github.com/bokyung124/infra-study/assets/53086873/0f4442fc-1793-4f2a-ad3b-0fe430a18833">

<br>

### 2) Amazon ECS - Fargate launch type

- 모두 서버리스 (관리할 EC2 인스턴스 없음)

<img width="291" alt="스크린샷 2023-08-25 오후 5 05 56" src="https://github.com/bokyung124/infra-study/assets/53086873/7649fba7-c322-4ba4-92e9-53c5ae1d6181">

<br>

### 3) Amazon ECS - Load balancer integrations

<img width="366" alt="스크린샷 2023-08-25 오후 5 07 40" src="https://github.com/bokyung124/infra-study/assets/53086873/60bfd3dc-41c5-4bb3-a584-98a2efd017e3">

<br>

## 9. ECS Service Auto Scaling

- 원하는 ECS 작업 수를 자동으로 늘리거나 줄임
- ECS 서비스 auto scaling (작업 수준) ≠ EC2 auto scaling (인스턴스 수준)
- 목표 추적, 단계 스케일링, 예약 스케일링

<br>

### Example

<img width="670" alt="스크린샷 2023-08-25 오후 5 10 25" src="https://github.com/bokyung124/infra-study/assets/53086873/1986b479-36d8-4b87-a12f-e5c8d860e699">

<img width="660" alt="스크린샷 2023-08-25 오후 5 10 46" src="https://github.com/bokyung124/infra-study/assets/53086873/2de452ef-2d38-4b0a-bfab-c06838ba139f">

<br>

## 10. Amazon EKS

- AWS에서 관리형 Kubernetes 클러스터를 시작하는 방법
- use case: 이미 회사에서 쿠버네티스를 사용하고 있고, 쿠버네티스를 사용하여 AWS로 마이그레이션을 원하는 경우
- 쿠버네티스는 클라우드에 구애받지 않음 (Azure, GCP 등 모든 클라우드에서 사용 가능)

<br>

## 11. 활용 사례

### 1) 이마트 - 모니터링 및 로그 관리

<img width="345" alt="스크린샷 2023-08-25 오후 5 37 41" src="https://github.com/bokyung124/infra-study/assets/53086873/e9019729-1e01-4759-a586-071166ed4f64">

<br>

### 2) 여기어때 - GitOps

<img width="671" alt="스크린샷 2023-08-25 오후 5 38 11" src="https://github.com/bokyung124/infra-study/assets/53086873/bcc687f5-9311-492c-a5a3-01d2ddfbe18e">