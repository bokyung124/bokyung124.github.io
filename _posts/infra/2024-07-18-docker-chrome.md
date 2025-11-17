---
title: "[DEV] docker 이미지에 chrome 설치"
last_modified_at: 2024-07-18T08:00:00-05:00
layout: post
categories:
    - Infra
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
tag: [docker, chrome]
---

## 문제

- 크롤링 스크립트를 비개발자가 언제든 실행할 수 있도록 자동화를 해야함
- AWS ECR - Batch - Lambda 를 이용해서 docker 이미지로 크롤링 스크립트를 올리고, lambda로 batch job을 실행하고자 함 
    - 크롤링 스크립트가 여러 개이고, 하나의 스크립트 실행 시간이 lambda의 time limit인 15분을 훌쩍 넘기 때문..

- 몇 개의 크롤링 과정에서 Selenium이 필요하기 때문에 docker 이미지에 크롬, 크롬 드라이버를 포함해주어야 했음!

### 오류 1

> arm64와 amd64의 혼동

- AWS Batch 작업의 CPU 아키텍처는 arm64 또는 x86_64(amd64) 중 선택할 수 있는데 아무 생각없이 모두 arm64로 설정했음
- BeautifulSoup을 사용하는 스크립트는 상관이 없었지만, 내가 설치한 크롬이 amd64에서 동작하는 파일이었기 때문에 오류 발생!
- Batch job을 x86_64로 변경

> `exec /usr/local/bin/python: exec format error` 오류

- 이것도 batch job과 docker 이미지의 아키텍처가 다르기 때문에 발생하는 오류!
- docker 이미지 빌드할 때 `--platform=linux/arm64` / `--platform=linux/amd64` 옵션을 지정해 설정할 수 있음
- dockerfile의 `FROM` 부분에 `--platform=linux/arm64` / `--platform=linux/amd64` 옵션을 추가할 수도 있음
    - `FROM --platform=linux/arm64 python:3.12 as build`


### 오류 2

> chrome 설치 오류

```
07/11/2024 06:29:47 p:INFO:Get LATEST chromedriver version for google-chrome
Traceback (most recent call last):
  File "/app/scripts/google_snippet.py", line 135, in <module>
    main()
  File "/app/scripts/google_snippet.py", line 128, in main
    google_snippet_df = get_google_snippet(get_keywords(google_sheet))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/scripts/google_snippet.py", line 74, in get_google_snippet
    service=Service(ChromeDriverManager().install()), options=chrome_options
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/webdriver_manager/chrome.py", line 40, in install
    driver_path = self._get_driver_binary_path(self.driver)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/webdriver_manager/core/manager.py", line 40, in _get_driver_binary_path
    file = self._download_manager.download_file(driver.get_driver_download_url(os_type))
                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/webdriver_manager/drivers/chrome.py", line 32, in get_driver_download_url
    driver_version_to_download = self.get_driver_version_to_download()
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/webdriver_manager/core/driver.py", line 48, in get_driver_version_to_download
    return self.get_latest_release_version()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/webdriver_manager/drivers/chrome.py", line 64, in get_latest_release_version
    determined_browser_version = ".".join(determined_browser_version.split(".")[:3])
                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'split'
```

- driver 설정 부분에서 chromedriver의 위치를 지정해주지 않고, 매번 새로 설치하도록 `service=Service(ChromeDriverManager().install())` 으로 지정했을 때 발생한 오류
- 설치된 크롬의 버전에 맞는 chromedriver를 자동으로 설치해주는건데,
    - 크롬이 도커 이미지에 잘 설치가 되지 않았거나
    - 설치된 크롬 버전이 126 버전이어서 그에 맞는 크롬 드라이버가 없기 때문에 오류가 발생한 것 같음

- 설치한 크롬의 위치는 `/usr/bin/google-chrome`인데, 버전을 `/usr/bin/chrome`에서 찾길래 dockerfile에서 심볼릭 링크를 생성해줌
    - `ln -sf /usr/bin/google-chrome /usr/bin/chrome`


### 오류 3

> chrome과 chromedriver 버전 오류

```
selenium.common.exceptions.WebDriverException: Message: Service /usr/local/bin/chromedriver unexpectedly exited. Status code was: 127
```

```
selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start: exited abnormally.
  (unknown error: DevToolsActivePort file doesn't exist)
  (The process started from chrome location /usr/bin/google-chrome is no longer running, so ChromeDriver is assuming that Chrome has crashed.)
```

```
DevToolsActivePort file doesn't exist
```

- 이전 크롤링 과정에서도 겪은 문제였는데.. 그새 또 이것 때문에 헤맸다
    - 위와 유사하게 크롬이 종료되었다거나, 크롬과 크롬 드라이버 버전이 맞지 않는다는 등의 오류가 발생할 수 있음


<br>

- 최신 크롬 드라이버 버전에 맞게 chrome, chromedriver 모두 114 버전으로 설치해주기로 함!
- 크롬 공식 사이트를 찾지 못해서 https://bestim.org/download/13218/?tmstv=1687251688 이 링크에서 직접 다운로드 -> 도커 이미지에 `COPY` 해주었음
- 이 방법으로 해결...! 이게 최선의 방법인지는 모르겠다


## 최종 dockerfile 예시

```dockerfile
FROM --platform=amd64 python:3.12
WORKDIR /app

# 환경변수 설정
ENV PATH="/usr/bin:/usr/local/bin:${PATH}"
ENV SHEET_URL="***"
ENV CHROME_BIN=/usr/bin/chrome 
ENV WDM_ARCH="aarch64"

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    xdg-utils \
    libxrandr2 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libx11-xcb1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    unzip \
    libu2f-udev \
    libvulkan1 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Google Chrome 114 버전 설치
COPY chrome_114.deb /tmp/google-chrome-stable.deb
RUN dpkg -i /tmp/google-chrome-stable.deb || apt-get install -fy

# ChromeDriver 다운로드 및 설치
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# 심볼릭 링크 생성
RUN ln -sf /usr/bin/google-chrome /usr/bin/chrome

ENV DISPLAY=:99

# 의존성 파일 복사 및 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 및 credential 파일 복사
COPY . /app
COPY client_secret.json /app/
COPY service-account.json /app/

CMD ["python", "scripts/google_snippet.py"]
```