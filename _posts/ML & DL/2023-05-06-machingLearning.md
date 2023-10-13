---
title: "[BoostCourse] 3. 머신러닝 기본 개념"
last_modified_at: 2023-05-07T22:19:00-05:00
layout: post
categories:
    - ML & DL
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
---

<br>

## 1. Underfitting & Overfitting

### fit
- 데이터를 __잘__ 설명할 수 있는 능력

- Underfitting: 데이터를 설명하지 못함
- Overfitting: 데이터를 과하게 설명함

<img width="485" alt="스크린샷 2023-05-07 오후 10 20 40" src="https://user-images.githubusercontent.com/53086873/236680022-67cbdff0-670c-4a6e-9b80-584e37511ed4.png">
- under - 적절 - over

<br>

### overfitting

<img width="258" alt="스크린샷 2023-05-07 오후 10 21 25" src="https://user-images.githubusercontent.com/53086873/236680071-3dbc4679-723d-4e70-b726-783e576ec98b.png">

<br>

- 우리의 데이터셋은 전체의 일부분
- 확보한 데이터셋을 이용해 전체 데이터셋으로 모델이 잘 돌아가게 하는 것이 목표

<img width="276" alt="스크린샷 2023-05-07 오후 10 23 05" src="https://user-images.githubusercontent.com/53086873/236680127-c590d008-ff93-4454-8e39-72e7dac0f970.png">

<br>

<img width="318" alt="스크린샷 2023-05-08 오전 12 56 36" src="https://user-images.githubusercontent.com/53086873/236688524-d1f6a242-3fe2-426c-b625-7aa20734988d.png">

- 빨간 선을 기준으로 현재 모델이 overfit인지 underfit인지 설명 가능

<br>

## 2. Regularization

<br>

### Early stopping
- validation error가 지속적으로 증가하는 지점에서 stop

<img width="339" alt="스크린샷 2023-05-08 오전 12 59 26" src="https://user-images.githubusercontent.com/53086873/236688663-f190560e-b95b-4b82-a0c4-af2bec75fde0.png">

<br>

### Parameter norm penalty
- Lasso, Ridge, ElasticNet penalty
- 패널티 계수 선택

<img width="510" alt="스크린샷 2023-05-08 오전 1 00 55" src="https://user-images.githubusercontent.com/53086873/236688734-9a8f7471-06b3-49f0-8d7b-36322cd7ab56.png">

<br>

### Data augmentation
- 이미지 문제를 풀 때 많이 사용
- 원본 이미지를 회전, 플립, 확대, 축소함으로써 데이터의 개수를 늘리는 방법

<img width="362" alt="스크린샷 2023-05-08 오전 1 03 40" src="https://user-images.githubusercontent.com/53086873/236688848-8b660b20-e6d6-497c-9c86-f7e58e4221b0.png">


<br>

#### SMOTE

<img width="638" alt="스크린샷 2023-05-08 오전 1 05 05" src="https://user-images.githubusercontent.com/53086873/236688923-b9b48c7f-fddd-4c0c-bef4-6c9af953b9fd.png">

- 불균형 데이터에 대해 augmentation
- 기준으로 설정된 데이터와 근처에 있는 데이터 사이에 새로운 데이터를 생성하는 방식

<br>

### Noise robustness

<br>

### Label smoothing

<br>

### Dropout

<img width="423" alt="스크린샷 2023-05-08 오전 1 06 36" src="https://user-images.githubusercontent.com/53086873/236688999-ac30d766-67d6-49b6-8e20-f9fba2aded4a.png">

- 원본 딥러닝 모델에서 무작위로 노드의 연결을 끊는 방식
- 피처의 일부분만 사용하여 모델을 생성하는 방법
- 정형 데이터 -> tree의 prouning

<br>

### Batch normalization

<br>

## 3. Validation strategy

<img width="653" alt="스크린샷 2023-05-08 오전 1 09 51" src="https://user-images.githubusercontent.com/53086873/236689142-80fd6e78-6a10-4a8e-bb16-739100ea5c8c.png">

<br>

### test set
- 프로젝트로 나오는 결과물과 직결되는 중요한 데이터셋

<img width="745" alt="스크린샷 2023-05-08 오전 1 10 16" src="https://user-images.githubusercontent.com/53086873/236689165-aa7c55c2-3d93-42cd-8f2b-33982fc4b47d.png">

- 최대한 전체 데이터셋을 대표할 수 있도록

<br>

### validation set
- 모델을 test set에 적용하기 전에, 모델을 파악하기 위해 이용하는 데이터셋
- test set과 최대한 유사하게 구성하는 것이 좋음

<img width="487" alt="스크린샷 2023-05-08 오전 1 15 13" src="https://user-images.githubusercontent.com/53086873/236689432-e4a9889c-a9b4-458f-88a9-cfd0cc0484c6.png">

<br>

- K-Fold    
<img width="545" alt="스크린샷 2023-05-08 오전 1 17 38" src="https://user-images.githubusercontent.com/53086873/236689551-733ed695-34c0-4631-b7d7-159667cb028f.png">