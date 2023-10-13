---
title: "[BoostCourse] 3. Gradient Descent Methods"
last_modified_at: 2023-05-27T18:20:00-05:00
layout: post
categories:
    - ML & DL
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
---

<https://www.boostcourse.org/ai111>

<br>

## Gradient Descent
- Stochastic gradient descent : 하나의 data
- Mini-batch gradient descent : data의 subset
- batch gradient descent : 전체 data

<br>

### Batch-size
- 보통 64, 128, 256 많이 사용하긴 하는데 중요한 파라미터임!
- 배치 사이즈를 작게 하는게 일반적으로 성능이 더 좋음 
    - flat minimum이 sharp minimum보다 좋음

<br>

<img width="562" alt="스크린샷 2023-05-27 오후 10 58 56" src="https://github.com/bokyung124/bokyung124.github.io/assets/53086873/33526129-8005-4189-b6ea-989b4d924ffd">


- 목표: testing function의 minimum을 찾는 것
    - flat minimum은 training function에서 조금 멀어져도 testing function에서도 적당히 낮은 값이 나옴     
        - train set에서 학습이 잘 되면 test set에서도 어느정도 잘 됨 : generalization performance가 높음
    - sharp minimum은 training set에서 local minimum에 도달했어도 testing function에서는 약간만 떨어져도 높은 값이 나옴

<br>

## Gradient Descent Methods

- Stochastic gradient descent
    - $W_{t+1} <- W_t - \eta g_t$
        - g: gradient
        - $\eta$: learning rate (step size)
    - 적절한 learning rate를 찾는 것이 어려움

- Momentum
    - $a_{t+1} <- \beta a_t + g_t$
    - $W_{t+1} <- W_t - \eta a_{t+1}$
        - $\beta$: momentum
        - a: accumulation (momentum이 포함된 gradient)
    - 이전 gradient의 방향을 어느정도 유지
    - gradient가 막 움직여도 어느정도 학습이 잘 됨

- Nesterov accelerated gradient
    - $a_{t+1} <- \beta a_t + \nabla L(W_t - \eta \beta a_t)$
    - $W_{t+1} <- W_t - \eta a_{t+1}$
        - $\nabla L(W_t - \eta \beta a_t)$: Lookahead gradient
    
- Adagrad
- Adadelta
- RMSprop
- Adam
