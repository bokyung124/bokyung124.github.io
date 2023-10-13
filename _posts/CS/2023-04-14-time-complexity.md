---
title: "[Algorithm] 시간 복잡도"
last_modified_at: 2023-04-09T16:30:00-05:00
layout: post
categories:
    - CS
excerpt: Inflearn) Do it! 알고리즘 코딩테스트 with JAVA 1강 
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
---

<br>

## 🍪 시간 복잡도 표기법
- 시간 복잡도: 문제를 해결하기 위한 연산 횟수
    - 일반적으로 1억 번의 연산을 1초의 시간으로 간주

<br>

### 시간 복잡도 정의
- 빅-오메가: 최선일 때의 연산 횟수
- 빅-세타: 보통일 때의 연산 횟수
- 빅-오: 최악일 때의 연산 횟수

<br>

```java
public class timeComplexityExample1 {
    public static void main(String[] args) {
        // 1~100 사이 값 랜덤 선택
        int findNumber = (int)(Math.random() * 100);

        for (int i = 100; i < 100; i++) {
            if (i == findNumber) {
                System.out.println(n(i));
                break;
            }
        }
    }
}

// 빅-오메가: 1
// 빅-세타: 2/N
// 빅-오: N
```

<br>

### 코딩테스트에서 사용하는 시간 복잡도 유형

- 코딩테스트에서 항상 **빅-오**를 기준으로 계산해야 함!
- 다양한 테스트 케이스를 수행해 모두 통과해야 하기 때문

<br>

- 빅-오 표기법의 수행 시간

<img width="345" alt="스크린샷 2023-04-14 오전 12 40 07" src="https://user-images.githubusercontent.com/53086873/231812505-87c2703f-fcb4-4666-a8f3-0b87fc097fc9.png">

<br>

#### 따져봐야 할 것

- 알고리즘 유형에 따라 
- 본인이 짠 코드가 얼마나 걸리는지

<br>

## 🍪 시간 복잡도 활용하기

### ex) 수 정렬하기 (BOJ 2750)

- 제한시간 2초 -> 2억 번 이하의 연산 횟수로 해결
- N개의 수가 주어졌을 때 오름차순 정렬
- 입력
    - 첫번째 줄에 N **(1 ≤ N ≤ 1,000,000)**
    - 두번째 줄부터는 N개의 줄에 숫자가 주어짐
- 출력
    - 1부터 N개의 줄에 오름차순 정렬한 결과 출력

<br>

#### 연산 횟수 = 알고리즘 시간 복잡도 x 데이터의 크기
- 버블 정렬(N²) -> (1,000,000)² : 2억보다 큼 (시간초과!)
- 병합 정렬(nlogn) -> (1,000,000)log(1,000,000) : 약 2억
- 데이터의 크기의 최댓값으로 따짐!

<br>

#### 시간 복잡도 바탕으로 코드 로직 개선
- 상수는 시간 복잡도 계산에서 제외
- 가장 많이 중첩된 **반복문**의 수행 횟수가 시간 복잡도의 기준이 됨

<br>

- ex) 연산 횟수가 N인 경우
```java
public class complexity1 {
    public static void main(String[] args) {
        int N = 100000;
        int cnt = 0;
        for(int i = 0; i < N; i++) {
            System.out.println('연산횟수: ' + cnt++);
        }
    }
}
```

<br>

- ex) 연산 횟수가 3N인 경우
```java
public class complexity2 {
    public static void main(String[] args) {
        int N = 100000;
        int cnt = 0;
        for(int i = 0; i < N; i++) {
            System.out.println('연산횟수: ' + cnt++);
        }
        for(int i = 0; i < N; i++) {
            System.out.println('연산횟수: ' + cnt++);
        }
        for(int i = 0; i < N; i++) {
            System.out.println('연산횟수: ' + cnt++);
        }
    }
}
```

- 두 코드의 연산 횟수는 3배 차이가 남
- 하지만, 코딩테스트에서는 일반적으로 상수를 무시하므로 두 코드 모두 시간 복잡도는 **O(n)**으로 같음!
    - 상수는 프로그램에서 실질적으로 엄청 큰 영향을 끼치지는 않음

<br>

- ex) 연산 횟수가 N²인 경우
```java
public class complexity3 {
    public static void main(String[] args) {
        int N = 100000;
        int cnt = 0;
        for(int i = 0; i < N; i++) {
            for(int j = 0; j < N; j++) {
                System.out.println('연산횟수: ' + cnt++);
            }
        }
    }
}
```

- 이중 for문이 전체 코드의 시간 복잡도의 기준이 됨 -> **O(n²)**
- 위의 예제처럼 일차 for문이 100개 더 있다해도 이중 for문 한 개를 기준으로 함

<br>


- 맞는 알고리즘 쓰기
- 시간 초과 -> 내 로직이 효율적으로 짜여있는지 확인
    - 가장 시간 복잡도를 크게 잡아먹는 부분!
