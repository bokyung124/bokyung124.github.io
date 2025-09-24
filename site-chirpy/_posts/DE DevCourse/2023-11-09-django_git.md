---
title: "[DEV] Django 협업"
last_modified_at: 2023-11-09T13:00:00-05:00
layout: post
categories:
    - Data Engineering
excerpt: 
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [DevCourse, TIL, Web]
---

## 1. 배경

- Django 프로젝트에서 팀원이 이미 개발하고 있던 웹 프로젝트를 받아서 협업해야 하는 상황
- 가상환경 위에서 개발 중이어서 그 가상환경을 그대로 이용하면 되겠다고 생각했는데, vscode에서 파이썬 인터프리터를 인식하지 못함
- 검색해보니 내 로컬에서 가상환경을 새로 만들어야 함을 알게됨!

## 2. 방법

### 1) 개발 상황

- 레포지토리 이름: tech_dashboard
- 가상환경 이름: techblog_dashboard
- 프로젝트 이름: techblog
- 앱 이름: techs

### 2) 레포지토리 클론

- 홈 디렉토리에 만들고자 함

```bash
cd ~
git clone [레포지토리 주소]
cd tech_dashboard
```

### 3) requirements.txt 생성

- 연동할 가상환경 폴더에서 생성

```bash
cd techblog_dashboard
pip list  ## 확인

pip freeze > requirements.txt
```

### 4) gitignore 생성

- 가상환경을 생성하면 매우매우 많은 파일이 생김 -> 올릴 필요 없음         
- <https://www.toptal.com/developers/gitignore> 에서 python, django, venv 입력하여 생성
- `.gitignore` 파일 생성 후 복붙 -> push

```bash
git branch requirements
git checkout requirements

git commit -m "add requirements.txt"
git push origin requirements
```

### 5) 내 가상환경 생성 및 접속

- 홈디렉토리에서

```bash
cd ~ 
python -m venv techblog_dashboard
source techblog_dashboard/bin/activate
```

### 6) requirements 적용

```bash
cd tech_dashboard/techblog_dashboard
pip install -r requirements.txt
```
