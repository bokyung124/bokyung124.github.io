---
title: "[kafka] 브로커, 복제, ISR(In-Sync-Replication)"
last_modified_at: 2023-04-14T07:02:00-05:00
layout: post
categories:
    - Kafka
excerpt: Inflearn) [데브원영] 아파치 카프카 for beginners
toc: true
toc_sticky: true
author_profile: true
mathjax: true
published: true
---

<https://www.inflearn.com/course/아파치-카프카-입문/dashboard>

<br>

## 🐳 Kafka Broker
- 카프카가 설치되어 있는 서버 단위
- 보통 3개 이상 브로커 사용 권장
- 파티션 1개, replication 1, 브로커 3대 -> 3대 중 한 대에 해당 토픽의 정보가 저장됨

<br>

## 🐳 Kafka Replication
- 파티션의 복제
- `1`이라면 파티션은 1개만 존재한다는 것
- `2`라면 파티션은 원본 1개와 복제본 1개로 총 2개 존재
- `3`이라면 파티션은 원본 1개와 복제본 2개로 총 3개 존재

<br>

- 브로커 개수에 따라 복제 개수 제한됨
    - 브로커 개수가 3이면 replication은 4가 될 수 없음

<br>

- 원본 파티션(1개)은 `Leader parition`이라고 부름
- 나머지 복제본은 `Follower partition`이라고 부름
- Leader와 Follower 파티션을 합쳐 `ISR (In Sync Replica)`라고 부름

<br>

### replication 사용 이유
- 파티션의 고가용성을 위해 사용
- 브로커가 3개인 카프카에서 replication, partition이 모두 1인 토픽 존재
    - 브로커가 갑자기 사용불가하게 된다면 더이상 해당 파티션은 복구할 수 없게됨
    - replication이 2라면 follower 파티션이 존재하므로, 복제본으로 복구 가능
        - follower -> leader parition 역할 승계

<br>

### 프로듀서의 ack 옵션
- 프로듀서가 토픽의 파티션에 데이터를 전달할 때 전달받는 주체가 `Leader partition`
- 프로듀서의 `ack` 상세옵션 : 고가용성 유지
    - `0` 옵션
        - 프로듀서는 leader 파티션에 데이터 전송하고 응답값을 받지 않음
        - leader 파티션에 데이터가 정상적으로 전송됐는지, 나머지 파티션에 정상적으로 복제됐는지 알 수 없고 보장할 수 없음
        - 속도는 빠르지만, 데이터 유실 가능성 존재
    - `1` 옵션
        - leader 파티션에 데이터 전송하고, leader 파티션이 데이터 정상적으로 받았는지 응답값 받음
        - 다만, 나머지 파티션에 복제되었는지는 알 수 없음
        - 데이터를 받은 즉시 브로커가 장애가 난다면 나머지 파티션에 데이터가 전송되지 못해 `0` 옵션과 같이 데이터 유실 가능성 존재
    - `all` 옵션
        - `1` 옵션에 추가로 follower에 복제가 잘 되었는지 응답값 받음
        - 데이터 유실은 없다고 보면 됨
        - `0`, `1`에 비해 확인하는 부분이 많기 때문에 속도가 현저히 느림

<br>

### 적정 replication 개수
- replication 개수가 많아지면 그만큼 브로커의 리소스 사용량도 늘어남
- 카프카에 들어오는 데이터량과, retention date(저장시간)을 잘 생각해서 replication 개수 결정
- 3개 이상의 브로커를 사용할 때 replication은 `3`으로 설정하는 것 추천