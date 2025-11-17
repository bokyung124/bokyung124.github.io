---
title: "디버깅"
last_modified_at: 2023-04-14T01:14:00-05:00
layout: post
categories:
    - Algorithm
excerpt: Inflearn) Do it! 알고리즘 코딩테스트 with JAVA 1강 
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
tag: [CS, 디버깅]
---

<br>

## 🧇 디버깅의 중요성
- **논리 오류**를 잡는 것이 중요!
- 디버깅: 프로그램에서 발생하는 문법 오류나 논리 오류를 찾아 바로잡는 과정

<br>

### 디버깅의 중요성
- index 범위, 데이터 타입 잘못 지정하는 등의 실수 -> 디버깅으로 해결 가능
- 디버깅은 코딩 테스트에 필요한 기술, 문제를 풀면서 반드시 해야 하는 과정!
- 보통 로그로 찍어 확인하는 경우가 많지만, 실제 코딩테스트에서 로그보다 디버깅이 유리

<br>

### 디버깅하는 법
- 1) 코드에서 디버깅하고자 하는 줄에 **중단점** 설정 (여러개 설정 가능)
- 2) **IDE의 디버깅 기능**을 실행하면 코드를 한 줄씩 실행하거나 다음 중단점까지 실행할 수 있으며, 이 과정에서 추적할 변수값도 지정할 수 있음
    - 이 방법으로 변수값이 자신이 의도한 대로 바뀌는지 파악
- 3) 변수값 이외에도 원하는 수식을 입력해 논리 오류를 파악할 수 있음

<br>

- 중단점에서 걸리면서 해당 시점에서의 변수 값 / 수식 등 보여줌
- `Window - Show View` 에서 설정 가능
    - ex) `Expressions` -> 수식 직접 입력해서 결과 확인 가능

<br>

## 🧇 디버깅 활용 사례

### ex) 구간 합 관련 코드

```java
import java.util.Scanner;

public class debuggingError {
    public static void main(String[] args) {
        // 배열에서 주어진 범위의 합을 구하는 프로그램
        Scanner sc  = new Scanner(System.in);
        int testcase = sc.nextInt();
        int answer = 0;
        int A[] = new int[100001];
        int S[] = new int[100001];

        for(int i = 0; i < 10000; i++) {
            A[i] = (int) (Math.random() * Integer.MAX_VALUE);
            S[i] = S[i-1] + A[i];
        }

        for(int t = 1; t < testcase; t++) {
            int query = sc.nextInt();
            for(int i = 0; i < query; i++) {
                int start = sc.nextInt();
                int end = sc.nextInt();
                answer += S[end] - S[start-1];
                System.out.println(testcase + " " + answer);
            }
        }
    }
}
```

<br> 

- **변수 초기화 오류**
    - `answer`의 초기화가 반복문 밖에 있어서 0으로 초기화되지 않음
        - 0이 아닌 기존의 값에 더해지기 때문에 이상한 값이 나옴
- **반복문에서 인덱스 범위 지정 오류 찾기**
    - 배열 크기 100001, 반복문은 10000 
        - 데이터가 다 들어가지 않음
- **잘못된 변수 사용 오류 찾기**
    - 출력 부분이나 로직 안에서 사용해야 하는 변수를 다른 변수와 혼동하여 잘못 사용하는 경우 
- **자료형 범위 오류 찾기**
    - 데이터 계산 도중 계산된 값을 변수에 저장할 때 변수에 짖어한 자료형 범위를 넘어가는 경우
    - 알고리즘을 잘 짰는데 값이 이상한 경우 자료형 먼저 바꿔보기!! (음수가 나오는 경우 등) (ex. int -> long) 
        - **자료형 처음부터 long형으로 선언하기!**
