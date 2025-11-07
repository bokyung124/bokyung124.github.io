---
title: "GCP 로드밸런서 설정 - Cloud Run Service"
last_modified_at: 2025-11-06T07:02:00+00:00
notion_page_id: 2a212b31-a8a8-80a0-98d8-fe5d175aadf1
layout: post
categories:
  - Dev
tags:
  - "GCP"
  - "Deploy"
  - "Django"
  - "Cloud Run Service"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

## **Google Cloud를 활용한 서버리스 웹 서비스 아키텍처 구축기**

GCP의 관리형 서비스를 조합하여 안정적인 웹 애플리케이션 아키텍처를 구축한 사례를 기록하고자 합니다. 프론트엔드와 백엔드 서버를 모두 **Cloud Run Service**에 배포하고, **로드밸런서**를 통해 트래픽을 관리하며, **Cloud CDN**을 이용해 이미지와 같은 정적 콘텐츠를 사용자에게 빠르게 전송합니다. 또한, 시간이 오래 걸리는 외부 API 호출 작업은 별도의 **Worker 서비스**를 통해 비동기적으로 처리하여 사용자 경험을 향상시켰습니다.

### 전체 아키텍처 개요

- **전역 외부 애플리케이션 부하 분산기:** 모든 사용자 트래픽의 진입점 역할을 합니다. 도메인 기반 라우팅, SSL 인증서 관리, HTTP에서 HTTPS로의 리디렉션 등을 처리합니다.

- **Cloud Run:** 프론트엔드, 백엔드, 그리고 비동기 작업을 처리하는 Worker 서비스를 배포하는 서버리스 플랫폼입니다. 트래픽에 따라 자동으로 확장 및 축소되어 비용 효율적입니다.

- **Cloud Storage & Cloud CDN:** 이미지 등의 정적 콘텐츠를 저장하고 전 세계 사용자에게 빠르게 전달하기 위해 사용됩니다.

- **Cloud Tasks:** 시간이 많이 소요되는 작업을 백엔드 서비스에서 분리하여 Worker 서비스로 비동기적으로 전달하는 데 사용됩니다.

### 전역 외부 애플리케이션 부하 분산기 설정

1. 프론트엔드 설정

외부로 부터 들어오는 모든 트래픽을 수신합니다. 어떤 IP 주소와 포트로 요청을 받을지, 통신을 어떻게 암호화할지 정의합니다.

- 고정 IP 주소 및 포트
  - 단일 고정 IP 주소를 생성하여 HTTPS에 연결합니다. 설정에서 HTTP 자동 리디렉션 설정을 추가합니다. 그럼 자동으로 `https-forwarding-rule-redirect` 이러한 형식의 HTTP url map 이 생성됩니다.

  - GCP 관리형 SSL 인증서를 생성합니다. Cloud DNS 에서 A 레코드에 구입한 도메인을 추가합니다.

![image](/assets/img/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-11-06_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_4.02.37.png)

**2. 백엔드 설정**

프론트엔드에서 받은 트래픽을 그대로 처리할 대상 그룹입니다. 본 아키텍처에서는 서로 다른 역할을 수행하는 4개의 백엔드 서비스를 정의하여 연결했습니다.

- **fe-service**: 프론트엔드 웹 앱
  - UI를 구성하는 프론트엔드 Cloud Run Service를 가리키는 서버리스 네트워크 엔드포인트 그룹(NEG)으로 구성됩니다.

- **be-service**: 메인 백엔드 API
  - 핵심 비즈니스 로직 API를 구현한 백엔드 Cloud Run Service를 가리키는 서버리스 NEG로 구성됩니다.

  - 백엔드 서버를 Cloud Run Service로 구성하는 경우, 프로덕션 서버의 `ALLOWED_HOST` 에 도메인뿐만 아니라 `127.0.0.1` 주소도 추가해야 합니다. 내부적으로 헬스체크를 진행하기 때문에 위 주소가 등록되지 않으면 500에러가 발생합니다.

- **worker-be-service**: 비동기 작업 워커
  - 외부 API 호출과 같이 오래 걸리는 작업을 전담하는 워커입니다. 메인 백엔드는 즉시 사용자에게 응답을 보내고, 워커 서버를 통해 백그라운드로 작업을 처리합니다.

  - 메인 백엔드와 동일한 이미지를 별도의 Cloud Run Service로 등록하였습니다. 해당 Cloud Run Service를 가리키는 서버리스 NEG로 구성됩니다.

- **storage-service**: 이미지 파일 서빙
  - GCS 버킷에 저장된 이미지를 사용자에게 빠르고 안전하게 전달하기 위해 Cloud CDN을 사용합니다.

  - 위 서비스들과 달리 인터넷 NEG를 사용하며, 백엔드로 GCS 버킷을 지정합니다.

  - GCS 버킷에 서비스 계정을 연결하여 HMAC 키를 생성합니다.

  - 백엔드 서비스에서 Cloud CDN을 설정한 후 위에서 생성한 HMAC 키를 등록하여 CDN을 통해 권한을 인증하도록 설정합니다. 
    ![image](/assets/img/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-11-06_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_1.39.21.png)

    - 이 부분은 서버에서 키를 인증하도록 추후 개선할 예정입니다. 이 경우 접속한 사용자 별로 이미지 접근 권한이 부여됩니다.

![image](/assets/img/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-11-06_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_1.39.06.png)

**3. 라우팅 규칙**

라우팅 규칙을 이용해 수신한 요청을 적절한 백엔드 서비스로 전달합니다. 이 규칙을 이용해 www 리다이렉트, https 리다이렉트, API 및 정적 파일 요청 등을 분리했습니다.

아래 순서에 따라 요청을 처리합니다.

1. **호스트 이름 확인 (gryyd.ai)**
  1. [`https://gryyd.ai`](https://gryyd.ai/) 또는 [`https://gryyd.ai`](https://gryyd.ai/) 로 사용자가 접속하면, `gryyd.ai` 호스트 규칙을 확인합니다.

  2. 이 규칙에는 URL 리디렉션이 설정되어 있습니다.
    1. **httpsRedirect: true** → HTTP 요청을 HTTPS 로 강제 전환합니다.

    2. **hostRedirect: www.gryyd.ai** → www가 없는 주소를 www.gryyd.ai 로 보냅니다.

  3. 결과적으로, 모든 gryyd.ai 요청은 최종적으로 https://www.gryyd.ai 로 영구 이동(301) 됩니다.

  <details markdown="1">
    <summary>경로 일치자 (host: gryyd.ai)</summary>
    ```yaml
    name: path-matcher-3
    defaultUrlRedirect:
      httpsRedirect: true
      hostRedirect: www.gryyd.ai
      redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
    ```
  </details>

2. **호스트 이름 및 경로 확인 (www.gryyd.ai)**
  1. 이제 [https://www.gryyd.ai](https://www.gryyd.ai/) 로 들어온 요청은 경로에 따라 다른 백엔드 서비스로 전달됩니다.
    1. `/api/generation/*` → worker 서비스로 이동하여 비동기 작업 실행

    2. `/api/*`, `/admin`, `/admin/*` → API 요청과 admin 페이지는 메인 백엔드 서버로 전달하여 요청 처리

    3. `/images/*`, `/assets/*` ,.. → 이미지 CDN URL은 스토리지 서비스로 전달하여 이미지 서빙

    4. 기타 모든 요청은 UI 상의 요청이므로 기본값인 프론트엔드 서버로 전달

  <details markdown="1">
    <summary>경로 일치자 (host: www.gryyd.ai)</summary>
    ```yaml
    defaultService: projects/{project_id}/global/backendServices/gryd-fe-service
    name: path-matcher-2
    pathRules:
    - paths:
      - /api/generation/*
      service: projects/{project_id}/global/backendServices/gryd-worker-be-service
    - paths:
      - /api/*
      - /admin
      - /admin/*
      service: projects/{project_id}/global/backendServices/gryd-be-service
    - paths:
      - /images/*
      - /thumbnails/*
      - /results/*
      - /assets/*
      - /references/*
      service: projects/{project_id}/global/backendServices/gryd-storage-service
    ```
  </details>

![image](/assets/img/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2025-11-06_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_1.40.12.png)

### Cloud Run 기반 서비스 배포

프론트엔드, 백엔드, Worker 서비스를 모두 Cloud Run에 배포하여 서버 관리에 대한 부담을 덜어냈습니다.

- **자동 확장/축소:** Cloud Run은 들어오는 요청 수에 따라 컨테이너 인스턴스 수를 자동으로 조절합니다. 트래픽이 없을 때는 0으로 축소되어 비용을 절감하고, 트래픽이 급증하면 신속하게 인스턴스를 늘려 안정적인 서비스를 제공합니다.
  - 배포 설정을 통해 최소, 최대 인스턴스 개수를 설정하여 예산에 맞게 조절할 수 있습니다.

- **서버리스 NEG 활용:** 각 Cloud Run 서비스는 '서버리스 네트워크 엔드포인트 그룹(Serverless NEG)'이라는 형태로 부하 분산기의 백엔드로 연결됩니다. 이를 통해 Google의 관리형 부하 분산 인프라와 서버리스 컴퓨팅 환경을 자연스럽게 연동할 수 있습니다.

### 비동기 작업 처리로 응답 속도 향상

Gemini API를 호출하여 콘텐츠를 생성하는 작업은 1분 이상의 시간이 소요될 수 있습니다. 이 시간동안 API 응답을 주지 않고 기다리게 하는 것은 UX 상 매우 좋지 않습니다.

이를 해결하기 위해 **Cloud Tasks**를 이용한 비동기 처리 방식을 도입했습니다.

1. 클라이언트가 콘텐츠 생성 요청을 백엔드(gryd-be-service)로 보냅니다.

2. 백엔드는 요청을 검증한 후, 실제 생성 작업을 담은 태스크(task)를 만들어 Cloud Tasks 큐에 추가하고 즉시 클라이언트에게 201 응답을 보냅니다.

3. Cloud Tasks는 이 태스크를 별도의 Worker 서비스(gryd-worker-be-service)의 특정 HTTP 엔드포인트로 전달합니다.

4. Worker 서비스는 태스크를 받아 시간이 오래 걸리는 생성 작업을 수행하고, 완료되면 그 결과를 데이터베이스에 저장합니다.

5. 생성 상태 관리는 데이터베이스의 `status` 컬럼을 통해 관리합니다. 사용자가 로딩 페이지에 접속하면 클라이언트는 polling API를 초 단위로 요청하여 완료 상태를 확인합니다.
  1. 이러한 구조를 통해 사용자는 생성 요청을 보낸 뒤 해당 페이지를 이탈할 수 있게 되어 사용자 경험이 좋아집니다.

  2. 다른 페이지에 갔다가 다시 생성한 페이지로 돌아온 경우, 생성 완료된 이미지를 확인할 수 있습니다.

이러한 방식을 통해 사용자는 무거운 작업의 결과를 기다릴 필요 없이 즉각적인 응답을 받을 수 있어 서비스의 반응성이 크게 향상됩니다.

### Cloud Storage와 Cloud CDN 연동

웹사이트의 로딩 속도는 사용자 만족도에 직접적인 영향을 미칩니다. 특히 이미지와 같은 용량이 큰 정적 콘텐츠는 로딩 속도의 주된 병목이 될 수 있습니다. 처음 개발 시에는 보안을 위해 매 응답마다 gcs 라이브러리를 통해 signed url을 생성하여 응답하도록 했습니다. 이는 생각보다 오랜 시간이 소요되었습니다.

이를 개선하기 위해 **Cloud CDN**과 연동된 부하 분산기를 통해 정적 파일을 서비스하도록 구성했습니다.

- 부하 분산기의 백엔드 서비스 중 하나인 gryd-storage-service는 특정 Cloud Storage 버킷을 가리키도록 설정되어 있습니다.

- 이 백엔드 서비스에서 **Cloud CDN을 활성화**하면, 사용자가 이미지를 요청했을 때 최초 요청 시에는 Cloud Storage에서 이미지를 가져오지만, 이후의 요청은 사용자와 가장 가까운 Google의 엣지 캐시에 저장된 복사본을 통해 전달됩니다.

- 이를 통해 데이터 전송 거리가 물리적으로 짧아져 지연 시간이 크게 줄어들고, 결과적으로 사용자는 이미지를 매우 빠르게 로딩할 수 있습니다.

### 마무리

Google Cloud의 전역 외부 애플리케이션 부하 분산기, Cloud Run, Cloud Tasks, 그리고 Cloud CDN과 같은 강력한 관리형 서비스들을 조합하여, 변화하는 트래픽에 유연하게 대응하고 사용자에게 빠르고 안정적인 경험을 제공하는 서버리스 아키텍처를 구축할 수 있었습니다. 각 컴포넌트가 명확한 역할을 가지고 독립적으로 운영되므로, 향후 서비스를 확장하거나 새로운 기능을 추가할 때에도 유연하게 대처할 수 있습니다.