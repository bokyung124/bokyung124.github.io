---
title: "[BITAmin] Multi Linear Regression"
last_modified_at: 2023-05-01T00:06:00-05:00
layout: post
categories:
    - ML & DL
excerpt: Multi Linear Regression
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
---

<br>

## 다중 선형 회귀
---

### 1. 기존 단순회귀모형의 문제점

- 종속변수를 설명하는 독립변수가 2개일 때 단순회귀모형을 사용하면 모형 설정이 부정확하고, 종속변수에 대한 중요한 설명변수가 누락될 수 있음   
- 즉, 계수추정량에 대해 bias가 발생   

<br>

### 2. 편향(Bias) & 분산(Variance)

- 편향-분산 트레이드 오프   
<img width="271" alt="스크린샷 2023-04-01 오후 10 40 07" src="https://user-images.githubusercontent.com/53086873/229292784-26620d3a-38bc-4ab8-968c-ae3423055d86.png">   
    - 편향이 낮고 분산이 적은 것이 가장 좋지만, 현실적으로 불가능   
    - 분산과 편향을 모두 고려한 최적의 복잡도를 찾아 적용하는 것이 바람직   

- bias 제거   
    - **독립변수를 추가**하여 회귀분석에서 예측에 영향을 미치는 중요한 요소 고려   
        - 단순회귀분석의 단점 극복 가능   
        - 다중선형회귀분석을 하는 이유   

<br>

### 3. 다중 선형 회귀

#### 1) 정의

- 2개 이상의 설명변수(독립변수)로 종속변수(반응변수)를 추정하는 회귀 분석   
- 회귀방정식을 기반으로 여러 원인 x를 사용하여 하나의 결과 y를 설명      

$$y_i = {\beta}_0 + {\beta}_1 x_{i1} + {\beta}_2 x_{i2} + ... + {\beta}_p x_{ip} + {\varepsilon}_i , i = 1,...,n$$
     
    - 설명변수 $x$ (feature) : p개   
    - 회귀계수 ${\beta}$ (parameter) : (p+1)개  

- ex) 인간관계($x_1$), 출퇴근거리($x_2$), 연봉($x_3$)이 회사생활만족도($y$)에 미치는 영향    

<br>

#### 2) 기본 가정  

- 선형성 (Linearity): 종속변수와 독립변수 사이에는 선형 관계가 있다.    
- 독립성 (Independency): 독립변수는 서로 linearly independent하다.    
- 정규분포성 (Multivariate normality): residual(잔차)이 정규분포를 따른다.    
- 등분산성 (Homoscedasticity): 분석하는 집단의 분산이 같다.    
- 독립변수들 간의 다중공선성이 없음 (Lack of Multicollinearity): 독립변수 간에 존재하는 상관관계가 없다.    

<br>

### 4. 다중공선성 확인하고 해결하기

- 확인 방법    
    - Variance Inflation Factor(VIF)    
    - Scatter plot    
- 다중공선성이 높으면 회귀계수의 표준오차가 비정상적으로 커짐 -> 추정치의 정확도가 낮아짐    
- 해결방법    
    - PCA를 적용해 독립변수 줄이기    
    - 데이터 많이 수집하기    
    - 다중공선성을 발생시키는 / 중요하지 않은 변수 제거하기    
    - 어떤 독립변수를 선택하는지가 중요!    
    - **변수선택법(Feature Selection)** 을 통해 적절한 독립변수만 남김     

<br>

### 5. 다항회귀 vs 다중회귀    

- 다항회귀 (polynomial regression)    
    - $weight = a {\times} length^2 + b {\times} length + c$       
    <img width="112" alt="스크린샷 2023-04-01 오후 10 58 27" src="https://user-images.githubusercontent.com/53086873/229293559-76ccd24f-e5a0-4a3d-b132-b8a94543402f.png">      
    - 독립변수의 차수가 높아짐    
    - 곡선형의 회귀모델    
    - 상호작용 특성 (interaction features)    

<br>

- 다중회귀 (multiple linear regression)    
    - $weight = a {\times} length + b {\times} height + c {\times} thickness + d {\times} 1$      
    <img width="109" alt="스크린샷 2023-04-01 오후 10 59 43" src="https://user-images.githubusercontent.com/53086873/229293639-4833d269-8a1c-429c-95ba-f79f5d479a19.png">   
    - 독립변수가 여러 개    
    - 고차원의 선형회귀모델    
    - 특성 공학 (feature engineering)     
        - 기존 특성을 사용해 새로운 특성을 뽑아내는 작업    