---
title: "[docker] 이미지 빌드"
last_modified_at: 2023-06-28T08:45:00-05:00
layout: post
categories:
    - Infra
excerpt: image build
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

## 1. 문제

- 컨테이너 이름: fortune:20.02
- Dockerfile에 포함될 내용
    - 베이스 이미지: debian
    - 컨테이너에 아래의 `webpage.sh` 파일 복사
    - 컨테이너에 fortune 애플리케이션 설치
    - 컨테이너 실행 시 저장한 `webpage.sh`가 실행되게 하기

- webpage.sh
```bash
#!/bin/bash
mkdir /htdocs
while :
do
    /usr/games/fortune > /htdocs/index.html
    sleep 10
done
```

<br>

## 2. Dockerfile 생성

```bash
FROM debian:latest
COPY webpage.sh /
RUN apt-get update
RUN apt-get install -y fortune
RUN ["chmod","+x","./webpage.sh"]  
CMD ["/webpage.sh"]
```

- webpage.sh 파일을 복사하면 권한이 없기 때문에 권한 부여해줘야 함

<br>

## 3. 이미지 build

```bash
cd fortune
docker build -t fortune:20.02 .
```

<img width="731" alt="스크린샷 2023-06-27 오전 9 42 21" src="https://github.com/bokyung124/infra-study/assets/53086873/b92890d4-13a5-4d23-b192-6064f29f99cf">

<br>

## 4. hub에 push

```bash
docker push fortune:20.02
```

---

### error   
`denied: requested access to the resource is denied` error

<br>

1) docker hub login
- docker hub 회원가입
- `docker hub login` 명령어 입력 후 username, pwd 입력

<img width="791" alt="스크린샷 2023-06-27 오전 9 54 04" src="https://github.com/bokyung124/infra-study/assets/53086873/afe4c278-7070-4aa9-ac08-f9eaad8d13d8">

<br>

2) docker image tag명 변경
- `docker image tag fortune:20.02 (username)/fortune:20.02`

<img width="794" alt="스크린샷 2023-06-27 오전 9 54 17" src="https://github.com/bokyung124/infra-study/assets/53086873/1df50704-1bb9-460d-b955-9a51cd2ed88c">

<br>

3) 다시 push
- `docker push (username)/fortune:20.02`

<img width="766" alt="스크린샷 2023-06-27 오전 9 54 25" src="https://github.com/bokyung124/infra-study/assets/53086873/8da04ca9-2cef-4114-a0e4-e0461fce193b">

<br>

4) docker hub에서 확인

<img width="1199" alt="스크린샷 2023-06-27 오전 9 54 48" src="https://github.com/bokyung124/infra-study/assets/53086873/56849214-7d16-4b45-8dcf-32b1bbde5c6e">