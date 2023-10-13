---
title: "[CS] REST API, RESTful API"
last_modified_at: 2023-04-04T20:57:00-05:00
layout: post
categories:
    - CS
excerpt: CS 1) API, REST API, RESTful API
author_profile: true
toc: true
toc_sticky: true
tag: [BE 이론]
---

<br>

## 🌱 API (Application Proframming Interface)
---

- 응용 프로그램에서 사용할 수 있도록 운영체제나 프로그래밍 언어가 제공하는 기능을 제어할 수 있게 만든 인터페이스 (위키백과)
- 처음부터 개발하거나 유지보수할 필요가 없는 외부 데이터와 기능에 접속하게 해줌
    - ex) 네이버 서비스에 나의 웹페이지를 공유하고 싶다면, 네이버에서 제공하는 공유하기 API를 이용하면 됨
    - ex) '날씨 앱'은 '기상청의 소프트웨어 시스템'과 API를 통해 대화하여 매일 최신 날씨 정보를 보여줌
- 한 프로그램에서 다른 프로그램으로 데이터를 주고받기 위한 방법, 현실에서 '메뉴판' 같은 것 (유튜브 '코딩애플')
    - ex) 웹툰서비스 API: 웹툰서버와 이용객이 웹툰을 주고받기 위한 방법 -> 코드로 이루어져 있음

<br>

### API가 가져야 할 내용

- 요청 방식 (method) (get/put)
- 무슨 자료를 요청할건지 (end point)
- 자료 요청에 필요한 정보 (parameter) (아이디, 이름 등)

<br>

### API 생성

- API 계획: 다양한 사용 사례를 미리 생각하고, API가 현재 API 개발 표준을 준수하는지 확인
- API 빌드: 상용 코드를 사용하여 API 프로토타입 생성
- API 테스트: 소프트웨어 테스트와 동일. 버그 및 결함을 방지하기 위해 수행
- API 문서화: API 문서는 사용 편의성을 높이는 가이드 역할   
- API 마케팅   

<br>
## 🌱 REST API 
---

- REpresentational State Transfer
- HTTP를 잘 사용하기 위한 아키텍처 스타일
- 오늘날 웹에서 가장 많이 사용되는 유연한 API
- 클라이언트가 서버 데이터에 엑세스하는데 사용할 수 있는 GET, PUT, DELETE 등의 함수 집합 정의
- 클라이언트와 서버는 HTTP를 사용하여 데이터 교환

<br>

### 과정

- 클라이언트가 서버에 요청을 데이터로 전송 
- 서버가 이 클라이언트 입력을 사용하여 내부 함수 시작
- 출력 데이터를 다시 클라이언트에 반환

<br>

### REST API의 필수 제약 조건

- Client-Server
    - 클라이언트는 서버에서 어떤 일을 수행하더라도 내부 작업을 알지 않아도 됨
    - 이는 플랫폼의 이식성 향상시킴
- Stateless
    - 클라이언트에서 서버로 하는 각 요청에는 그 요청에 필요한 모든 정보가 포함되어야 함
- Cache
    - 요청에 대한 응답 내의 데이터에 해당 요청은 캐시가 가능한지 불가능한지 명시해야 함
    - 보통 HTTP Header에 `cache-control` 헤더 이용
- Uniform Interface

<br>

### Uniform Interface

- URL로 지정된 리소스에 대한 조작을 통일하고 한정된 인터페이스로 수행하는 아키텍처 스타일
- 제약조건
    - Resource-Based
    - Manipulation Of Resources Through Representations
    - Self-Descriptive Message: API 문서가 REST API 응답 본문에 존재해야 함 (적어도 어디에 있는지)
    - **Hypermedia As the Engine Of Application State (HATEOAS)**
        - Hypermedia(링크)를 통해서 애플리케이션의 상태 전이가 가능해야 함
        - 또한, Hypermedia(링크)에 자기 자신에 대한 정보가 담겨야 함

<br>

### REST API 사용의 이점

- 통합: 새로운 애플리케이션을 기존 소프트웨어 시스템과 통합하는 데 사용
- 혁신: 새로운 앱의 등장으로 전체 산업이 바뀔 수 있음. 전체 코드를 다시 작성할 필요 없이 API 수준에서 변경 가능
- 확장: 다양한 플랫폼에서 고객의 요구 사항을 충족할 수 있도록 지원
- 유지 관리의 용이성: 두 시스템 간의 게이트웨이 역할 -> API가 영향을 받지 않도록 내부적으로 시스템 변경 -> 한 시스템의 코드 변경이 다른 시스템에 영향 미치지 않음

<br>

## 🌱 RESTful API
---

- REST한 방식으로 클라이언트와 서버간 상호 데이터 교환을 하는 API
- HTTP를 잘 사용하기 위해, URI와 HTTP 메소드를 사용해서 URL로 어떤 자원에 접근할 것인지, 메소드로 어떤 행위를 할 것인지 표현하여 설계한 API

<br>

### RESTful API로 간주되기 위한 조건

- 클라이언트-서버 커뮤니케이션: 요청 간에 클라이언트 정보가 저장되지 않으며, 각 요청이 분리되어 있고 서로 연결되어 있지 않음
- Stateless(무상태): 서버가 요청 간에 클라이언트 데이터를 저장하지 않음
- **즉, 클라이언트는 서버를 신경 쓸 필요 없이 API 호출만 하면 원하는 결과를 받을 수 있음**

<br>

### RESTful API의 장점

- 보기 좋음: URL만 보고 어떤 자원에 접근할 것인지, 메소드를 보고 어떤 행위를 할 것인지 알 수 있어 개발에 용이함
- 자원 효율적 이용: 한 개의 URI로 3개의 행위(CRUD)를 명시할 수 있어 효율적
- **무상태 유지**: 다양한 브라우저와 모바일에서 통신할 수 있도록 함. 클라이언트가 서버에 종속되지 않아도 되기 때문에, scale out한 상황에서도 용이함