---
title: "[BoostCourse] 2. 최적화"
last_modified_at: 2023-05-26T18:20:00-05:00
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

<https://www.boostcourse.org/ai111>

<br>

## Introduction

## Gradient Descent
- 편미분을 통해 loss function의 local minimum을 찾는 과정

<br>

## Important Concepts

- Generalization    
    <img width="372" alt="스크린샷 2023-05-26 오후 6 56 46" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/2062cf4f-df2a-4aab-aa18-f20e4abe3063">

    - 일반화 성능을 높이는 것이 목적
    - 일반화 성능: how well the learned model will behave on unseen data
    - generalization gap: training error와 test error의 차이
    - **이 network의 학습 데이터의 성능과 비슷하게 나올 것이다**

<br>

- Under-fitting vs Over-fitting   
    <img width="378" alt="스크린샷 2023-05-26 오후 6 58 47" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/b90470d0-d9cf-4ff1-8afd-1d1f6a77efc5">

<br>

- Cross validation   
    <img width="233" alt="스크린샷 2023-05-26 오후 7 04 54" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/c6313dc6-46d8-4f18-95ed-0af934ca8ae0">

    - train data와 validation data를 나눠서 학습
    - 학습에 사용되지 않은 validation data를 얼마나 잘 예측하는지
    - 최적의 hyperparameter 찾을 때 이용 -> 이후 모든 데이터를 학습에 사용
    - test data는 cross validation에 사용하지 않음 (학습에 절 대 사용되지 않음!!)

<br>

- Bias-variance tradeoff   
    <img width="286" alt="스크린샷 2023-05-27 오후 9 05 45" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/ee504791-424e-4a07-8696-34788d9fdcd3">

    - variance: 입력을 넣었을 때 출력이 얼마나 일관적으로 나오는지
        - 낮을수록 일관적 -> overfitting
    - bias: 모델을 통해 얻은 예측값과 실제값의 차이의 평균
        - 클수록 예측값과 정답 간의 차이가 큼 -> underfitting

    - **cost**를 minimize 해야 함
        - cost = $E[(t-\hat{f})²]$
        - cost는 bias², variance, noise로 구성되어 있기 때문에 어느 하나가 작아지면 다른 하나가 커지는 trade-off 관계

<br>

- Bootstrapping
    - any test or metric that uses random sampling with replacement
    - 학습데이터 중 몇 개만 활용한 모델을 여러개 만들 때, 모델들이 만들어낸 예측값들의 consistence를 보고 전체적인 모델의 성능 예측

<br>

- Bagging and Boosting
    - Bagging (Bootstrapping aggregating)   
        - 여러개의 모델을 bootstrapping하여 결과 평균
    - Boosting
        - 예측을 잘 못한 학습 데이터에 대해 잘 동작하는 모델 생성
        - weak learner 여러 개 -> 하나의 strong learner

    <img width="459" alt="스크린샷 2023-05-27 오후 10 28 31" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/50f9e3b8-7fb6-4d0d-845a-b3cbff9cf9bd">
