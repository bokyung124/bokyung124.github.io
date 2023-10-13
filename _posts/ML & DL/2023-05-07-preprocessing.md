---
title: "[BoostCourse] 2. 정형데이터 전처리"
last_modified_at: 2023-05-07T19:20:00-05:00
layout: post
categories:
    - ML & DL
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
tag: [study, Boostcourse, DL]
---

## 1. 데이터 전처리
- 데이터를 머신러닝 모델에 입력하기 위해 적절히 처리하는 과정
- EDA / 모델이나 목적에 따라 달라지는 데이터 전처리
- 선형 모델인지, 트리인지, 딥러닝인지 등에 따라 방식 달라짐

<br>

### 연속형 변수

#### Scaling
- 데이터의 단위 또는 분포 변경
- 선형 기반의 모델의 경우 변수들 간의 scale을 맞추는 것이 필수적

<br>

- Min Max Scaling
- Standard Scaling
- Robust Scaling

<img width="266" alt="스크린샷 2023-05-07 오후 9 03 47" src="https://user-images.githubusercontent.com/53086873/236676274-b4d346f9-72e7-4f02-8511-3f9424528121.png">

#### Scaling + Distribution

- Log transformation    
    - 정규분포에 가깝게
<img width="498" alt="스크린샷 2023-05-07 오후 9 06 05" src="https://user-images.githubusercontent.com/53086873/236676391-395f677a-15f2-4790-9524-cab3391af586.png">   

- Quantile transformation   
    - 값을 uniform하게 / 정규분포에 맞추어
<img width="509" alt="스크린샷 2023-05-07 오후 9 10 29" src="https://user-images.githubusercontent.com/53086873/236676639-13eae294-6b7e-4954-a0da-51c7cc2459f2.png">

<br>

<img width="540" alt="스크린샷 2023-05-07 오후 9 09 57" src="https://user-images.githubusercontent.com/53086873/236676604-649937ec-31db-42ef-b269-20e883cc4d58.png">

#### Binning
    - 연속형 -> 범주형
    - overfitting 방지
<img width="416" alt="스크린샷 2023-05-07 오후 9 10 53" src="https://user-images.githubusercontent.com/53086873/236676655-9eddea44-7d28-46e8-8e34-bc71e851301d.png">

<br>

### 범주형 변수

- 보통 문자형으로 되어있어 머신러닝 모델의 입력 변수로 사용할 수 없음 -> 수치형 변수로 변환

#### Encoding

- One hot encoding
    - 변수를 1과 0으로 변환
    - 변수가 많으면 차원의 저주 발생
<img width="460" alt="스크린샷 2023-05-07 오후 9 12 58" src="https://user-images.githubusercontent.com/53086873/236676743-7037ac8f-3455-41ef-b2d7-34aba2345637.png">

<br>

- Label encoding
    - 한개의 컬럼에서 범주마다 각기 다른 값을 갖도록 변환
    - 모델이 숫자의 순서를 특징으로 인식할 수 있는 문제
<img width="377" alt="스크린샷 2023-05-07 오후 9 14 10" src="https://user-images.githubusercontent.com/53086873/236676807-3f488e1d-209f-4c17-a4ac-b4f93197a644.png">

<br>

- Frequency encoding
    - 해당 변수의 값이 나오는 빈도수를 변수의 값으로 지정
<img width="684" alt="스크린샷 2023-05-07 오후 9 15 12" src="https://user-images.githubusercontent.com/53086873/236676863-395cebb9-29cd-4901-ad7e-a9a32307268c.png">


<br>

- Target encoding
    - 각각의 범주가 가지는 타겟 변수의 평균을 값으로 지정
    - 서로 다른 범주이지만 같은 값을 갖게 될 수 있음
    - 새로 생기는 범주에 대해서는 값을 지정하기 어려움
    - overfitting 발생 가능
<img width="716" alt="스크린샷 2023-05-07 오후 9 16 31" src="https://user-images.githubusercontent.com/53086873/236676927-39813462-8ee6-4fd2-a849-a72855d177f8.png">

<br>

- Embedding

<br>

## 2. 결측치 처리

### Pattern
- 결측치 패턴을 파악해서 규칙이 있는지 확인

<img width="673" alt="스크린샷 2023-05-07 오후 10 02 31" src="https://user-images.githubusercontent.com/53086873/236679204-1eec2daf-b5e1-4e12-81a8-eb32dfa0c794.png">

### Univariate
- 제거
- 평균값 삽입
- 중위값 삽입
- 상수값 삽입

<img width="539" alt="스크린샷 2023-05-07 오후 10 07 11" src="https://user-images.githubusercontent.com/53086873/236679410-b35b8019-5cc8-4fcb-b53d-2235d99fcbf0.png">


### Multivariate
- 회귀분석
- KNN nearest

<img width="569" alt="스크린샷 2023-05-07 오후 10 10 42" src="https://user-images.githubusercontent.com/53086873/236679563-962fa2d1-22ed-42ee-bcd6-9705be6dcf78.png">

<br>

## 3. 이상치

<img width="495" alt="스크린샷 2023-05-07 오후 10 13 05" src="https://user-images.githubusercontent.com/53086873/236679680-abec8a79-591c-4ea2-9966-0a89f6b63771.png">

### 이상치 탐지

- Z-Score
- IQR

### 이상치 처리
- 정성적
    - 이상치 발생 이유 파악
    - 이상치 의미 파악
- 성능적
    - Train Test Distribution 