---
title: "[docker] 도커 기초"
last_modified_at: 2023-06-26T08:45:00-05:00
layout: post
categories:
    - Infra
excerpt: docker basic
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [study, docker]
---

## 1. docker
- code
- services
- database
- libraries

<img width="545" alt="스크린샷 2023-06-21 오후 11 11 26" src="https://github.com/bokyung124/k8s-study/assets/53086873/c2462a0e-779b-4c94-b0e7-65e196ce8dea">

<br>

## 2. docker의 필요성

### 1. 'It works on my machine' 문제
- predictable
- consistent

<img width="506" alt="스크린샷 2023-06-21 오후 11 12 25" src="https://github.com/bokyung124/k8s-study/assets/53086873/cde66978-e39a-4219-a3ea-08211363a13f">

<br>

### 2. DevOps의 등장, 마이크로서비스 아키텍처
- fast
- scalable

<br>

#### 1) 마이크로 서비스 아키텍처

<img width="530" alt="스크린샷 2023-06-21 오후 11 14 34" src="https://github.com/bokyung124/k8s-study/assets/53086873/0de283df-f06c-49ef-9643-f92341cc74f6">

<img width="546" alt="스크린샷 2023-06-21 오후 11 17 40" src="https://github.com/bokyung124/k8s-study/assets/53086873/71598def-5f17-4e0c-9e09-d21e98ec1669">

<br>

- 마이크로서비스 아키텍처는 애플리케이션이 서비스 모음으로 개발되는 애플리케이션 아키텍처의 한 유형

- 마이크로서비스를 사용하면 대규모 애플리케이션을 각각 담당 영역을 가진 소규모의 독립적인 구성요소로 구분할 수 있음 

<br>

## 3. 도커란
- 애플리케이션을 개발, 배포 및 실행하기 위한 오픈소스 플랫폼
- 가상화 기술 중 하나인 **컨테이너화** 기술을 사용하는 도구 
    - 가상화: 서버, 스토리지, 네트워크 및 기타 물리적 시스템에 대한 가상 표현을 생성하는 데 사용할 수 있는 기술
    - 가상 소프트웨어는 물리적 하드웨어 기능을 모방하여 하나의 물리적 머신에서 여러 가상 시스템을 동시에 실행
- 애플리케이션을 **컨테이너** 단위로 격리하고 번들링

<br>

- 기존 virtual machine과의 차이

<img width="604" alt="스크린샷 2023-06-21 오후 11 20 05" src="https://github.com/bokyung124/k8s-study/assets/53086873/5b459a0d-9711-4144-a05a-caa1921fdbdb">

    - vm과 다르게 Host OS를 공유
    - Bins/Libs도 공유
    - 기존의 가상화로만은 한계가 있어 등장한 것이 컨테이너화!

<br>

## 4. 도커 아키텍처

<img width="627" alt="스크린샷 2023-06-21 오후 11 51 50" src="https://github.com/bokyung124/k8s-study/assets/53086873/f14dbd53-ad47-4bc6-8fc3-67526726a4f9">

<br>

- 레지스트리
    - 도커 이미지를 저장하는 저장소 역할
    - `docker pull`, `docker run`과 같은 명령어를 실행하면 도커는 사용자가 요청한 이미지를 도커 레지스트리에서 찾아옴
    - `docker push` 명령어를 실행하면 도커는 이미지를 레지스트리에 저장
- 도커 호스트
- 도커 클라이언트
    - 도커 서버와 통신하기 위한 가장 중요한 기능 수행
    - 도커 데몬에 명령 전달하기 위한 수단
    - 도커 명령어를 사용하면 Docker API가 REST API 형식으로 데몬의 소켓에 전달됨
- 이미지
    - 컨테이너를 생성하기 위해 필요한 절차를 기록한 파일
    - 레이어(명령어)를 중첩하여 쌓는 방식으로 생성
    - read-only
    - 이미지를 만들기 위한 명령어 집합인 docker file을 빌드하여 생성
- 컨테이너
    - 이미지를 실행한 결과로 생성되는 인스턴스
    - 사용자는 도커 클라이언트의 명령어를 호출함으로써 컨테이너를 관리할 수 있음
- 도커 데몬 (dockerd)
    - 클라이언트의 명령을 REST API로 받아 이미지, 컨테이너, 네트워크, 볼륨 등의 도커 오브젝트 관리
    - 호스트에 설치됨
- 도커 CLI

<br>

## 5. 컨테이너 동작 방식

<img width="778" alt="스크린샷 2023-06-26 오전 7 52 18" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/c531bbbd-d078-455d-a59d-23a701027850">

<br>

- 도커 호스트와 hub가 있음 
- hub는 컨테이너 이미지를 저장해 놓은 창고
- 도커 호스트 위에는 도커 데몬이 동작 중 -> 도커 클라이언트 명령 실행 가능

- 도커 데몬에게 명령을 요청하는 **도커 서치커맨드**를 데몬에게 요청
    `$ docker search nginx  # 도커 허브에 nginx가 있는지 찾아봐줘`

- 도커 데몬은 도커 허브에 nginx가 있는지 확인해서, 있으면 리스트 출력

- 해당 **컨테이너 이미지** 가져옴
    `$ docker pull nginx:latest`

- 이미지의 레이어 수만큼의 폴더로 파일이 저장됨 (레이어 한 개당 폴더 한 개)

- 도커 **컨테이너 동작**
    `$ docker run -d [--name web -p 80:80 nginx:latest]`

- 이제 도커 컨테이너 이미지가 도커 데몬 위에서 컨테이너화되어 현재 실행중인 application이 됨
- 위의 예시의 경우, 80번 포트에(localhost, ip or host name) 연결하면 nginx가 웹페이지를 고객에게 보냄 
    - 고객이 접속할 수 있는 서버를 컨테이너 기반으로 만든 것!

<br>

## 6. 도커 이미지, 컨테이너, docker files

|이미지|도커|
|---|---|
|컨테이너의 청사진|이미지를 실행한 객체|
|컨테이너를 빌드하기 위한 read-only files|호스트 머신의 다른 모든 프로세스와 격리된 머신의 sandboxed process|
|애플리케이션 및 사전 구성된 환경 패키지화 </br> 모든 종속성, 구성, 스크립트, binary 등|자체 소프트웨어, binaries, configurations를 운영하고 실행하기 위해 이미지에서 제공하는 격리된 파일 시스템 사용|
|도커 파일로부터 만들어짐|도커 이미지로부터 만들어짐|
|서로 다른 환경(개발, 테스트, 프로덕션)에서 공유할 수 있고, 다른 팀 구성원 간에 또는 심지어 공개적으로 공유할 수 있는 재사용 가능한 구성 요소|일반적으로 개별 환경 또는 호스트에 연결|
|도커파일의 각각의 스텝은 이미지 안에 새로운 레이어 생성 </br> 이 레이어들은 나눠져 저장되므로, 이미지 간 공유될 수 있고, 공간을 절약할 수 있음|컨테이너가 시작될 때 이미지의 모든 레이어가 메모리에 로드되므로, 컨테이너는 이미 이미지의 크기보다 더 많은 시스템 리소스를 사용할 수 있음|
|**Immutable** </br> 일단 이미지가 생성되면 변경할 수 없음|상태를 가질 수 있음(start, stop, pause) </br> 실행 중인 컨테이너에 명령을 실행하여 상태를 바꿀 수 있음|
||컨테이너 안에 데이터를 저장할 수는 있지만, 컨테이너가 제거되면 해당 데이터는 손실됨 </br> 컨테이너 인스턴스 간에 또는 컨테이너가 제거된 후에도 유지되어야 하는 데이터는 docker volume이나 바인드 마운트를 사용하는 것이 좋음|

<br>

<img width="849" alt="스크린샷 2023-06-26 오전 8 05 03" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/b9423d80-5f14-460e-ac55-d249ebe07b71">

<br>

## 7. 자주 쓰이는 도커 명령어

[docker docs](https://docs.docker.com/engine/reference/commandline/cli/)

<br>

|명령어|설명|예시|
|---|---|---|
|docker search|도커 허브에서 이미지 검색|docker search nginx|
|docker pull|docker 이미지를 레지스트리로부터 다운로드|doekr pull nginx:latest </br> docker pull ubuntu:18.04|
|docker run|docker 이미지를 기반으로 새로운 컨테이너 실행|docker run -d -p 80:80 my_container nginx </br> docker run -it ubuntu bash|
|docker ps|현재 실행중인 도커 컨테이너 보기|docker ps|
|docker stop|실행중인 도커 컨테이너 정지|docker stop my_container|
|docker rm|도커 컨테이너 삭제|docker rm my_container|
|docker rmi|도커 이미지 삭제|docker rmi nginx:latest|
|docker build|docker file을 기반으로 도커 이미지 생성|docker build -t my_image . </br> docker build -t my_image:20.02 /workingdir|
|docker images|현재 시스템에 있는 도커 이미지 보기|docker images|
|docker exec|실행중인 도커 컨테이너에 명령 실행|docker exec -it ubuntu bash|
|docker logs|도커 컨테이너 로그|docker logs ubuntu|
|docker push|생성한 이미지를 원격 저장소(도커허브)에 업로드|docker push username/my_image:20.02|

<br>

## 8. Dockerfile 작성하기
- 이미지를 빌드하는 데 필요한 모든 명령이 순서대로 포함된 텍스트 파일

```bash
# syntax=docker/dockerfile:1
FROM ubuntu:18.04
COPY . /app
RUN make /app
CMD python /app/app.py
```

- `FROM`: 컨테이너의 베이스 이미지 (운영환경)
- `COPY`: 도커 클라이언트의 현재 디렉터리에서 '/app' 디렉터리로 파일 복사
- `RUN`: 컨테이너 빌드를 위해 베이스 이미지에서 실행할 명령어 (이 경우 `make /app`)
- `CMD`: 컨테이너 안에서 실행할 특정 명령어나 스크립트 지정