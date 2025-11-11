---
title: "CORS"
last_modified_at: 2025-11-11T02:10:00+00:00
notion_page_id: 2a812b31-a8a8-8099-ad2b-e7b2d73ccddd
layout: post
categories:
  - CS
tags:
  - "Web"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

## CORS (Cross-Origin Resource Sharing)

한 출처 (Origin) 에서 실행중인 웹 애플리케이션이 **다른 출처의 리소스에 접근할 수 있도록** 브라우저에 알려주는 체제입니다.

웹 브라우저는 보안상의 이유로 **동일 출처 정책 (Same-Origin Policy, SOP)** 을 따르는데, 이 정책은 스크립트가 자신이 속하지 않은 다른 출처의 리소스와 상호작용하는 것을 제한합니다.

예를 들어, `https://example.com` 이라는 웹사이트에서 `https://api.another-domain.com` 에 있는 데이터를 요청하는 것은 다른 출처 간의 요청이므로 동일 출처 정책에 의해 기본적으로 차단됩니다. CORS는 이러한 제한을 완화하여 특정 조건 하에 다른 출처의 리소스 요청을 안전하게 허용하는 메커니즘을 제공합니다.

### CORS의 주요 구성 요소

- **출처 (Origin)**: 프로토콜, 호스트 (도메인), 포트 번호의 조합입니다. 이 중 하나라도 다르면 다른 출처로 간주됩니다.

- **HTTP 헤더**: CORS는 추가적인 HTTP 헤더를 사용하여 동작합니다. 클라이언트는 요청 헤더에 `Origin` 을 담아 보내고, 서버는 응답 헤더에 `Access-Control-Allow-Origin` 을 포함하여 응답합니다.

### CORS 동작 방식

크게 3가지 시나리오로 나뉩니다.

1. **단순 요청 (Simple Request)**: 특정 조건을 만족하는 간단한 요청입니다. 브라우저는 먼저 서버에 요청을 보낸 후, 서버가 응답 헤더에 `Access-Control-Allow-Origin` 값을 보내주면 브라우저가 현재 출처와 비교하여 리소스 접근 허용 여부를 결정합니다.

2. **프리플라이트 요청 (Preflight Request)**: 본 요청을 보내기 전에 `OPTIONS` 메서드를 사용하여 예비 요청을 보내는 방식입니다. 예비 요청을 통해 서버가 실제로 해당 요청을 수락할 수 있는지 확인하고, 안전하다고 판단될 때 본 요청을 보냅니다.

3. **인증 정보를 포함한 요청 (Credentialed Request)**: 쿠키나 인증 헤더와 같이 인증 정보를 포함하여 다른 출처에 요청을 보낼 때 사용됩니다. 이 경우 서버는 `Access-Control-Allow-Credentials` 헤더를 `true` 로 설정해야 합니다.

## Access-Control-Allow-Origin

이 헤더는 **서버가 발행하는 출입 허가증**이라고 볼 수 있습니다. 어디에서 온 요청까지 서버에 들어오는 것을 허락할지 정보를 담습니다. 브라우저는 이 값을 보고 요청을 보낸 페이지가 허가된 곳인지 아닌지를 최종적으로 판단하여 데이터를 보내줄지 말지 결정합니다.

### 동작 과정

- 구성 요소
  - 웹페이지: `https://my-site.com`
  - API 서버: `https://api.server.com`
  - 브라우저

1. **클라이언트 (브라우저) 의 요청**

    1) 웹페이지의 JavaScript 코드가 API 서버에 요청을 보내고자 합니다.

    2) 브라우저는 API 서버에 요청을 보내면서, 요청 헤더에 `Origin` 을 자동으로 추가합니다.

    3)  `Origin`은 브라우저의 URL (== 웹페이지 주소) 값을 갖습니다.
      ```bash
      GET /data HTTP/1.1
      Host: api.server.com
      Origin: https://my-site.com
      ```

2. **API 서버의 응답**

    1) 서버는 요청을 받고, 서버에 설정된 CORS 정책을 확인합니다.
        - 서버 개발자가 미리 작성해둔 규칙입니다.

    2) 이 규칙에 따라 서버는 응답을 보낼 때 응답 헤더에 `Access-Control-Allow-Origin` 값을 포함시킵니다.
    ```bash
    HTTP/1.1 200 OK
    Access-Control-Allow-Origin: https://my-site.com
    Content-Type: application/json
    ```

    3) 이 출처 (`https://my-site.com`) 는 우리 리소스에 접근해도 좋다는 의미입니다.

3. **브라우저의 최종 확인**

    1) 브라우저는 서버로부터 이 응답을 받고 `Origin` 값과 `Access-Control-Allow-Origin` 값을 비교합니다.

    2) 두 값이 일치하면 허가된 요청으로 판단하고, 서버가 보내준 데이터를 웹페이지의 JavaScript 코드에 안전하게 전달해줍니다.

    3) 브라우저가 일종의 경비원 역할을 하는 것입니다.
    
    4) 만약 서버가 `Access-Control-Allow-Origin: https://another-site.com` 으로 응답했다면, 브라우저는 데이터를 즉시 폐기하고 콘솔에 CORS 오류를 띄웁니다.

### Access-Control-Allow-Origin 값의 종류

이 헤더에는 크게 3가지 종류의 값을 설정할 수 있습니다.

1. **특정 출처 1개 명시**
    - **값**: `https://my-site.com`
    - **의미**: 오직 `https://my-site.com` 이라는 출처에서 온 요청만 허용합니다. 가장 일반적이고 보안상 권장되는 방식입니다.
    - **주의**: 프로토콜 (http, https), 도메인, 포트까지 정확하게 일치해야합니다. `http://my-site.com` 이나 `https://www.my-site.com` 에서 온 요청은 거부됩니다.

2. **모든 출처 허용**
    - **값**: `*`
    - **의미**: 어떤 출처에서 온 요청이든 상관없이 모두 허용합니다. 
    - **사용처**: 외부에 완전히 공개된 API, 누구나 사용해도 되는 웹 폰트나 이미지 파일 등에 사용됩니다.
    - **주의**: 로그인 정보 (쿠키, 인증 토큰) 가 필요한 민감한 요청에는 이 설정을 사용할 수 없습니다. 브라우저가 보안상의 이유로 막습니다.

3. **동적 값 설정**
    - **값**: `Access-Control-Allow-Origin` 헤더 자체는 하나의 값만 가질 수 있습니다. `https://a.com, https://b.com` 과 같은 목록은 불가능합니다.
    - **해결책**: 서버에서 요청의 `Origin` 헤더 값을 읽은 뒤, 서버에 미리 정의된 허용 목록에 해당 `Origin` 값이 포함되어 있는지 확인합니다. 만약 포함되어 있다면, `Access-Control-Allow-Origin` 헤더의 값으로 **요청을 보낸 그 Origin 값**을 넣어서 응답합니다.

`Origin` 과 `Access-Control-Allow-Origin` 헤더는 브라우저와 서버가 서로 신원과 규칙을 확인하며 안전한 교차 출처 통신을 가능하게 하는 핵심적인 약속(프로토콜)입니다.