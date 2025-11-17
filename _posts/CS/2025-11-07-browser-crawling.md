---
title: "[CS] 브라우저 렌더링 방식에 따른 크롤링 전략"
last_modified_at: 2025-11-07T06:21:00+00:00
notion_page_id: 2a412b31-a8a8-800f-87bc-de5b274b0195
layout: post
categories:
  - CS
tags:
  - "Crawling"
  - "Web"
  - "Python"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

## **1. SSR (Server-Side Rendering) / SSG (Static Site Generation)**

### **특징**

- 서버가 데이터가 완전히 채워진 완성된 HTML 문서를 클라이언트에 응답으로 보냅니다.

- 페이지 소스에 최종적으로 보이는 모든 텍스트 콘텐츠가 포함되어 있습니다.

### **크롤링 전략: 정적 분석 (Static Analysis)**

이 방식은 가장 간단하고 효율적인 크롤링이 가능합니다. JavaScript 렌더링 과정이 필요 없기 때문입니다.

- **핵심 도구:**
  - `requests`: HTTP 요청을 보내 HTML 문서를 받아오는 라이브러리

  - `BeautifulSoup` 또는 `lxml`: 받아온 HTML 문서를 파싱(parsing)하고, 원하는 데이터를 CSS Selector나 XPath를 이용해 추출하는 라이브러리

### **Python 예시 코드**

```python
import requests
from bs4 import BeautifulSoup

# 대상 URL (SSR/SSG로 가정)
url = "<https://ssr-example-website.com/products/123>"

# 1. HTTP GET 요청으로 HTML 문서 가져오기
try:
    response = requests.get(url)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error during requests to {url} : {e}")
    exit()

# 2. BeautifulSoup으로 HTML 파싱하기
soup = BeautifulSoup(response.text, 'html.parser')

# 3. CSS Selector를 이용해 원하는 데이터 추출하기
product_name = soup.select_one("#product-name-h1").get_text(strip=True)
price = soup.select_one(".price-tag > span").get_text(strip=True)
description = soup.select_one("div.product-description").get_text(strip=True)

# 4. 결과 출력
print(f"상품명: {product_name}")
print(f"가격: {price}")
print(f"설명: {description}")
```

## **2. CSR (Client-Side Rendering) / App Shell + CSR**

### **특징**

- 서버는 내용이 거의 비어있는 뼈대 HTML과 JavaScript 파일 링크를 응답으로 보냅니다.

- 브라우저에서 JavaScript가 실행되어 API 서버와 통신하고, 받아온 데이터로 동적으로 페이지 콘텐츠를 생성합니다.

- 초기 HTML 소스에는 원하는 데이터가 존재하지 않습니다.

### **크롤링 전략: 동적 분석 (Dynamic Analysis) / 브라우저 자동화**

JavaScript를 실행하여 최종 렌더링된 HTML을 얻어야 하므로, 실제 웹 브라우저를 제어하는 자동화 도구가 필요합니다.

- **핵심 도구:**
  - `Selenium`: 가장 널리 알려진 브라우저 자동화 프레임워크. WebDriver를 통해 Chrome, Firefox 등 실제 브라우저 제어

  - `Playwright`: Microsoft에서 개발한 최신 브라우저 자동화 라이브러리. 빠르고 안정적이며 비동기 API 지원

  - `Puppeteer` (Pyppeteer): Google에서 개발한 Chrome 제어 라이브러리의 Python 포트

### **Python 예시 코드 (Playwright)**

```python
from playwright.sync_api import sync_playwright, TimeoutError

# 대상 URL (CSR로 가정)
url = "<https://csr-example-website.com/dashboard>"

def run(playwright):
    browser = playwright.chromium.launch(headless=True) # headless=False로 브라우저 동작 확인 가능
    context = browser.new_context()
    page = context.new_page()

    try:
        # 1. 페이지로 이동 (내부적으로 JS 로딩 및 렌더링 대기)
        page.goto(url, wait_until="networkidle")

        # 2. 특정 요소가 렌더링될 때까지 명시적으로 대기 (필수)
        # 이 요소는 API 호출이 완료된 후에만 DOM에 나타남
        page.wait_for_selector("#user-profile-card h2", timeout=5000)

        # 3. 렌더링이 완료된 페이지의 HTML 콘텐츠를 가져옴
        content = page.content()

        # 4. (선택) Playwright의 Locator를 직접 사용해 데이터 추출
        user_name = page.locator("#user-profile-card h2").inner_text()
        email = page.locator("p.user-email").inner_text()

        print(f"사용자 이름: {user_name}")
        print(f"이메일: {email}")

    except TimeoutError:
        print(f"Timeout: 지정된 시간 내에 요소를 찾지 못했습니다. 페이지가 제대로 로드되지 않았을 수 있습니다.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.close()

# Playwright 실행
with sync_playwright() as playwright:
    run(playwright)
```

## **3. API 직접 호출을 통한 데이터 수집**

브라우저 자동화(Selenium, Playwright)는 JavaScript를 렌더링 할 수 있지만, 실제 브라우저를 구동하기 때문에 리소스 소모가 크고 속도가 느립니다. 더 빠르고 안정적인 방법은 웹사이트의 프론트엔드(React, Vue 등)가 내부적으로 사용하는 API를 직접 호출하여 정제된 데이터를 얻는 것입니다.

이 방식은 별도의 인증이 필요할 수 있기 때문에 인증 로직 파악 및 테스트가 필요합니다.

### **1) API 엔드포인트 탐색**

가장 먼저 어떤 API 요청을 통해 데이터를 가져오는지 찾아내야 합니다.

1. 크롤링하려는 페이지에서 개발자 도구(F12)를 엽니다.

2. **'Network' 탭**으로 이동합니다.

3. **'Fetch/XHR' 필터**를 클릭합니다. 이 필터는 JavaScript가 비동기적으로 서버와 통신하는 내역만 보여줍니다.

4. 상호작용 이후 호출되는 API가 있을 수 있기 때문에 페이지를 새로고침하거나, 데이터를 불러오는 동작(예: 스크롤, 버튼 클릭)을 수행합니다.

5. 요청 목록에서 원하는 데이터를 포함하고 있을 것으로 보이는 요청을 클릭하여 **'Response'(응답)** 또는 **'Preview'(미리보기)** 탭에서 실제 데이터를 확인합니다.

### **2) 요청 분석**

성공적인 API 응답을 받기 위해 서버에 어떤 정보를 보내야 하는지 분석합니다. 해당 요청의 **'Headers'(헤더) 탭**을 유심히 봐야 합니다.

- **Request URL:** 호출해야 할 API의 주소(엔드포인트)입니다.

- **Request Method:** `GET`, `POST` 등 HTTP 메서드를 확인합니다.

- **Request Headers:** 서버가 정상적인 요청으로 판단하는 데 필요한 인증 정보나 메타데이터가 포함됩니다.
  - `Authorization`: `Bearer eyJhbGci...` 와 같은 JWT 인증 토큰이 포함될 수 있습니다.

  - `Cookie`: `sessionid=...; csrftoken=...;` 와 같이 사용자의 로그인 세션을 증명하는 쿠키 정보가 포함됩니다.

  - `User-Agent`: 브라우저 및 운영체제 정보. 일부 서버는 이 값이 없으면 요청을 차단합니다.

  - `Referer`: 현재 페이지의 URL (CSR인 경우). CSRF 방어 로직에 사용될 수 있습니다.

  - 기타 커스텀 헤더 (`X-Requested-With`, `X-CSRF-Token` 등)

### **3) 코드로 요청 복제**

분석한 정보를 바탕으로 `requests` 라이브러리를 사용하여 HTTP 요청을 그대로 재현합니다.

### **Python 예시 코드 (로그인 후 대시보드 데이터 가져오기)**

대시보드 페이지에서 프로젝트 목록을 가져오는 API(`https://api.example.com/projects`)를 찾아냈다고 가정합니다. 이 API는 로그인 쿠키와 인증 토큰을 필요로 합니다.

```python
import requests
import json

# Step 1: 분석한 API 엔드포인트 URL
api_url = "<https://api.example.com/v1/projects?user_id=123>"

# Step 2: 분석한 Request Headers를 딕셔너리로 구성
# 개발자 도구에서 'Copy as cURL' 또는 'Copy request headers'를 활용하면 편리합니다.
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "Cookie": "sessionid=a1b2c3d4e5f6g7h8; theme=dark",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Referer": "<https://example.com/dashboard>",
}

# Step 3: requests 라이브러리로 API 직접 호출
try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # 200 OK가 아니면 예외 발생

    # Step 4: JSON 응답 파싱
    # .json() 메소드는 JSON 문자열을 Python 딕셔너리로 자동 변환해줍니다.
    data = response.json()

    # Step 5: 데이터 처리 및 출력
    print("성공적으로 데이터를 가져왔습니다.")
    print(f"총 프로젝트 개수: {data['total_count']}")

    for project in data['projects']:
        print(f"- 프로젝트명: {project['name']} (ID: {project['id']})")

except requests.exceptions.HTTPError as errh:
    print(f"Http Error: {errh}")
    print(f"Response Body: {response.text}") # 오류 원인 파악에 중요
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
except json.JSONDecodeError:
    print("Error: 응답이 유효한 JSON 형식이 아닙니다.")
    print(f"Raw Response: {response.text}")
```

### **핵심 고려사항 및 주의점**

1. **인증(Authentication):** API 크롤링의 가장 큰 허들입니다. `Authorization` 헤더나 `Cookie`를 요청에 포함시켜야 합니다. 이 값들은 보통 로그인 API를 먼저 호출하여 얻거나, 개발자 도구에서 임시로 복사하여 테스트해야 합니다.
    - 주로 유효 기간이 있기 때문에 이 값을 주기적으로 Refresh 하는 작업이 필요할 수 있습니다.

2. **동적 헤더(Dynamic Headers):** 일부 사이트는 보안을 위해 매번 바뀌는 `X-CSRF-Token` 같은 헤더를 사용합니다. 이 경우, HTML 페이지를 먼저 요청하여 토큰을 파싱한 후, API 요청 헤더에 포함시켜야 하는 다단계 프로세스가 필요할 수 있습니다.

3. **API Rate Limiting (요청 제한):** 짧은 시간에 너무 많은 요청을 보내면 서버가 IP를 일시적 또는 영구적으로 차단할 수 있습니다. 요청 사이에 `time.sleep()`을 넣어 적절한 간격을 두는 것이 중요합니다.

4. **API 변경 위험:** 웹사이트가 공식적으로 제공하는 Public API가 아닌 이상, 내부 API는 언제든지 예고 없이 변경될 수 있습니다. API 구조가 바뀌면 크롤러 코드를 수정해야 합니다.