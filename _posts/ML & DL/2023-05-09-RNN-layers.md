---
title: "[Udemy] RNN (2)"
last_modified_at: 2023-05-09T13:30:00-05:00
layout: post
categories:
    - ML & DL
excerpt: Layers, Input, Output
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
---

<https://hanium.udemy.com/course/keras-deep-learning/learn/lecture/9359716#reviews>

<br>

## RNN 
---

<img width="1219" alt="스크린샷 2023-05-09 오후 2 03 31" src="https://user-images.githubusercontent.com/53086873/236998654-8acb7a8c-8d10-47a3-8032-2f93fe867761.png">

<br>

- 가진 데이터의 종류에 따라, 어떻게 학습시키고 싶은지에 따라
- Many to One
    - Input 여러개 - 한개의 Output
    - 가장 많이 사용
- Many to Many
    - Input 여러개 - 여러개의 Output
- One to Many
    - Input 한개 - 여러개의 Output
- One to One
    - Input 한개 - 한개의 Output

<br>

## Gradient vanishing 문제
---

<img width="687" alt="스크린샷 2023-05-09 오후 2 08 00" src="https://user-images.githubusercontent.com/53086873/236999233-38fda2db-eae5-4ab6-a05c-07e9d365e721.png">

<br>

- time step: RNN의 개수
- time step이 무한정 늘어나면 gredient vanishing 문제 발생
- 층이 깊어질수록 상대적으로 처음에 있는 weight와 bias의 영향력(gradient)이 사라지는(vanishing) 문제
    - DNN과 마찬가지

- Yn에 error가 있을 때 H0의 문제가 반영될 수 있는지
- 일반적으로 200~300 정도면 time step 적절하다고 판단

<br>

## LSTM, GRU Layer
---

- LSTM (Long Term Short Memory)
    - Gradient Vanishing 문제를 해결할 수 있도록 RNN Cell을 변형한 구조
```python
model = Sequential()
model.add(LSTM(256, input_shape=(10, 1,)))
model.add(LSTM(256))
```

<br>

- GRU (Gated Recurrent Unit)
```python
model = Sequential()
model.add(GRU(256, input_shape=(10, 1, )))
model.add(GRU(256))
```

<br>

## Input, Output shape
---

<img width="936" alt="스크린샷 2023-05-09 오후 2 32 28" src="https://user-images.githubusercontent.com/53086873/237002963-98d16e82-59a9-4ef8-b771-f6ec9b561882.png">

<br>

### Input (N Sample, N time step, N feature)

<br>

- DNN과 다른 점: time step이 추가됨
- 3차원으로 형태를 만들어 Input을 주어야 함!
- sample 개수는 생략 가능

<br>

- Case 1
    - input feature 4개
    - 4개 feature가 3개의 time step에 들어감
    - LSTM Layer를 추가할 때 input shape를 3 time step, 4 feature으로 넣어주어야 함!

- Case 2
    - 4개의 time step, feature 1개

- 코드를 짤 때에는 그림이 없기 때문에 머릿속으로 생각해놓아야 함
- 모든 RNN Layer는 (sample, time step, feature)!

<br>

### Output

- (N Sample, N time step, Value) 
    - return_sequences == True
    - __Many to One__

- (N Sample, Value)
    - return_sequences == False
    - __Many to Many__
    - x와 동일한 shape으로 y를 주어야 함 -> time step 고려 필요!

<br>

### ex1 ) Many to One
<img width="471" alt="스크린샷 2023-05-09 오후 2 40 00" src="https://user-images.githubusercontent.com/53086873/237004105-6329701a-4713-42c6-8c27-167737e0f03d.png">

<br>

<img width="369" alt="스크린샷 2023-05-09 오후 2 41 32" src="https://user-images.githubusercontent.com/53086873/237004324-9a9a22cb-51bb-4401-af60-82ffef7f0bb5.png">

- 2개의 데이터, 각각의 데이터는 4개의 time step, 각각의 time step은 하나의 feature 가짐
- X 배열에 2개의 데이터, 4개의 time step, feature는 1개

- **batch** 
    - 실제 fit으로 훈련할 때 batch 설정
    - keras는 default로 32 이용
    - RNN에서는 배치 사이즈 지정해주는 것이 좋음
    - 총 2개의 데이터 -> batch 1 / 2

<br>

<img width="313" alt="스크린샷 2023-05-09 오후 2 41 51" src="https://user-images.githubusercontent.com/53086873/237004379-f835d606-6194-4072-9c94-67d049bee834.png">

- Many to One

<br>

### ex2 ) Many to Many
<img width="900" alt="스크린샷 2023-05-09 오후 2 45 55" src="https://user-images.githubusercontent.com/53086873/237005011-20945a46-813b-4b20-8cfd-87fe7f645885.png">

- `return_sequences=True`로 하지 않으면 RNN 레이어를 겹쳐서 이용할 수 없음
    - 모든 레이어는 같은 차원의 입력을 받아야 하는데, 첫번째 레이어의 Output이 1개로 나오면 다음 레이어로 들어갈 수 없음 

