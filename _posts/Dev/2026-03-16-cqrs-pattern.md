---
title: "CQRS 패턴"
last_modified_at: 2026-03-16T02:47:00+00:00
notion_page_id: 32512b31-a8a8-80bf-bbdb-ed38746c9b1e
layout: post
categories:
  - Dev
tags:
  - "Design Pattern"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

## CQRS 

Command and Query Responsibility Segregation

- 시스템에서 데이터의 상태를 변경하는 작업 (Command)과 데이터를 조회하는 작업 (Query)의 책임을 분리하는 아키텍처 패턴

전통적인 CRUD 모델에서는 하나의 데이터베이스가 읽기와 쓰기를 모두 처리함

→ 읽기 요청량과 쓰기 요청량의 불균형, 복잡한 join으로 인한 성능 저하 발생

→ 쓰기 모델과 읽기 모델을 물리적 / 논리적으로 분리하게 됨!

### Command DB (OLTP)

- 비즈니스 로직의 트랜잭션을 처리하고 데이터의 정합성을 보장

- 데이터 중복을 피하기 위해 정규화된 스키마를 가짐

- 강력한 트랜잭션을 지원하는 RDBMS를 주로 사용

### Query DB (OLAP)

- 사용자의 복잡한 조회 요청을 빠르게 반환

- join 연산을 최소화하기 위해 비정규화된 스키마로 저장 (화면에 보여질 형태 그대로)

- Elasticsearch, NoSQL, 캐싱용 Redis, 읽기 전용 RDBMS Replica 등을 주로 사용

### 데이터 동기화 파이프라인

Data Sync & Message Broker

- Command DB에 발생한 변경 사항을 Query DB로 전달

- 구현 방식
  - [**CDC**](https://bokyung124.github.io/posts/cs/cdc/): Debezium 등을 활용해 Command DB의 트랜잭션 로그를 읽어와 Kafka로 전송

  - **Event Sourcing**: 상태 변경 자체를 이벤트로 정의하여 Kafka 등 Event Store에 Append-Only로 저장하고, 이를 컨슈밍하여 Query DB 업데이트

## 데이터 파이프라인 관점

### 비정규화 파이프라인 구축 (Stream Processing)

- CQRS 구조에서 Query DB는 join을 하지 않도록 비정규화 되어있어야 함

- Kafka Streams, Apache Flink, Spark Streaming 등을 사용해 스트림 단계에서 여러 데이터 소스를 join하고 가공하여 하나의 완성된 도큐먼트로 만들어 Query DB에 넣는 작업을 수행

### Eventual Consistency (최종적 일관성) 관리

- 물리적으로 DB를 분리하면, Command DB에 데이터가 반영된 시점과 Query DB에 데이터가 동기화되는 시점 사이에 미세한 시간 차이가 발생함 → **최종적 일관성**

- Kafka 등 메시지 큐의 처리 지연을 모니터링하고, 데이터 유실 없이 순서가 보장되도록 파이프라인을 설계해야 함
  - ex. Kafka 파티션 키를 사용자 ID로 지정하여 순서 보장

### Polyglot Persistence

- CQRS는 하나의 DB를 고집하지 않고, 목적에 맞는 DB를 골라씀

- 이 때 여러 DB를 이어주는 것이 메시지 브로커 기반의 실시간 데이터 파이프라인!

### Event Sourcing과의 결합

- 이벤트 소싱 기반의 CQRS는 모든 데이터 변경 이력 (이벤트)을 보관하기 때문에, 특정 시점으로 Query DB를 다시 구축할 수 있음 → **불변 데이터 (Immutable Data) 원칙**

- 과거 데이터를 백필해야 하는 상황에 매우 유용!

## CQRS 장단점

### 장점

- **독립적인 확장성**: 읽기 트래픽이 폭증하면 Query DB만 확장하면 됨

- **성능 최적화**: 조회 시 복잡한 join이 필요없기 때문에 쿼리 응답 속도가 비약적으로 향상됨

- **데이터 모델의 자유도**: 쓰기 용도의 정규화 모델과 읽기 용도의 비정규화 모델을 타협없이 각각 최적화할 수 있음

### 단점 (주의점)

- **높은 아키텍처 복잡도**: 관리해야 할 DB와 인프라 (Kafka, CDC 시스템 등)가 늘어나고, 모니터링 포인트가 증가함

- **데이터 동기화 지연**: 쓰기 직후 조회했을 때 아직 Query DB에 동기화되지 않아 이전 데이터가 보일 수 있음 (최종적 일관성 문제) → 클라이언트에서 처리하거나 감수해야 함