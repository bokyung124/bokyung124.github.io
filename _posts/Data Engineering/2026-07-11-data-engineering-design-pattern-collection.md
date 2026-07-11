---
title: "[책] 데이터 엔지니어링 디자인 패턴 - 데이터 수집 디자인패턴"
last_modified_at: 2026-07-11T11:14:00+00:00
notion_page_id: 39a12b31-a8a8-80f6-a9ea-eb64ad6f01db
layout: post
categories:
  - Data Engineering
tags:
  - "Data Engineering"
  - "Book"
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
---

# 데이터 수집

## 전체 적재

- 상황
  - 데이터베이스 부트스트랩

  - 참조 데이터셋 생성

- 데이터셋에 마지막 갱신 값이 존재하지 않는 상황

- 변경이 잦지 않고 행 수가 많지 않은 경우

- EL 로 해결할 수 있지만, 이종 데이터베이스 간 데이터를 적재해야 한다면 추출과 적재 사이에 변환 계층이 필요
  - ETL 잡이 됨
    - 데이터 크기 문제: 데이터 크기의 변동이 클 경우 하드웨어 제한때문에 실패할 수 있음 → 오토스케일링 기능 활용

    - 데이터 일관성 문제: 삭제 및 삽입 작업으로 교체할 경우 삽입 전 데이터셋을 조회하면 일관성이 깨질 수 있음 → 트랜잭션 / 단일 데이터 노출 추상화로 해결

- 활용
  - aws s3: 버킷 복제 + 목적지 파일 정리
    - `aws s3 sync {input} {output} --delete`
      - `--delete` : 원본에 없지만 목적지에 있는 파일 삭제

  - spark + delta lake
    ```python
    input_data = spark.read.schema(input_data_schema).json({input})
    input_data.write.format("delta").save({output})
    ```

    - delta lake를 사용하면 트랜잭션 및 버전 관리 기능 → 일관성 문제 해결

    - spark: 인프라를 확장하면 데이터 크기가 급격하게 변동되어도 수집 잡에 영향없이 확장 가능

  - 버전 관리 기능이 없는 DB (ex. postgresql) + airflow : 버저닝 테이블 + view 교체
    ```sql
    COPY devices_${version} FROM {input_file} CSV DElIMETER ';' HEADER;
    CREATE OR REPLACE VIEW devices AS SELECT * FROM devices_${version}
    ```

## 증분 적재

### 증분 로더

지속적으로 증가하는 데이터셋

- **델타 컬럼**: 마지막 실행 이후 추가된 레코드 식별 (ex. 이벤트 기반 데이터 → 수집 시간)
  - 매 실행마다 워터마크를 유지함. 다음 실행에서는 `WHERE {델타컬럼} > {마지막_워터마크}` 조건으로 새 데이터 수집

  - 프로듀서 → 적재 테이블 적재 (랜딩테이블, S3, Kafka 등, 이때 수집 시간 추가) → 최종 타겟 테이블로 적재할 때 수집 시간 조건으로 필터링
    - 수집 시간이라는 것은 반드시 컬럼일 필요는 없고, S3 등의 경우 파일이 적재된 시각 / Kafka의 경우 메시지의 오프셋 등 도착 순서/도착 시점을 나타내는 무언가이면 됨

  - *주의*: 이벤트 시간을 델타 컬럼으로 사용하는 것은 위험. 이미 처리한 이벤트 시간에 대한 지연된 데이터를 전송할 경우, 수집 프로세스 상에서 해당 레코드가 누락될 수 있음
    - 이벤트가 발생한 순서와 데이터가 도착하는 순서가 일치하지 않을 수 있음!

    - 수집 시간을 델타 컬럼으로 쓰면 워터마크는 데이터가 시스템에 들어온 시각 기준으로 움직임 → 지연 데이터에도 문제없음

- **시간 분할 데이터셋**: 시간 기반 분할을 사용해 수집할 새로운 레코드 집합 감지 (파티션 기반)
  - 새로운 파티션 수집이 보장되도록 ‘준비 마커’ 패턴 사용

  - 실행 일자로부터 처리할 파티션을 암묵적으로 해결할 수 있음 (ex. 로더가 11시에 실행되면 이전 시간의 파티션을 대상으로 처리할 수 있음)


광고 플랫폼은 이미 준 수치를 나중에 소급 수정함 → lookback window 기법 필요
최근 N일 데이터를 upsert

이 경우 순수 워터마크 방식을 사용하면 지연/수정된 값이 누락되거나 틀린 채로 남음

그래도 raw 데이터에 `_loaded_at` 같은 적재 시각 컬럼을 남겨두면 디버깅에 유용

API → BigQuery Raw Data 적재하는 구조에서는 BigQuery Raw 테이블 자체가 랜딩 테이블 역할
여기에 수집 시간 컬럼 추가 → 이후 DW/DM 가공에서 `WHERE _loaded_at > 워터마크` 로 증분 처리 가능

S3/Kafka는 스트리밍 데이터나 도착 순서를 별도로 관리해야 할 때 사용. 일배치 API 에서는 불필요.

- 문제
  - 물리 삭제 문제
    - 삭제된 레코드에는 델타 컬럼이 없음 → 논리 삭제 사용 (delete 대신 update)

  - 백필링
    - 증분 로더는 작은 델타만 처리하도록 설계 → 백필을 하기엔 리소스가 부족할 수 있음

    - 수집 윈도우 제한으로 해결할 수 있음 (소량씩 가져오도록 분할)

- Airflow: `FileSensor` 를 이용하여 다음 파티션이 가용해지기를 기다릴 수 있음
  - 파티션을 닫는다: 업스트림이 워터마크 선을 긋는 행위 (ex. 수집 시간 기준으로 파티셔닝 → 해당 파티션 데이터가 다 차면 완료 마커 남김)

  ```markdown
  프로듀서: dt=2026-07-11 파티션에 데이터 다 씀 → 완료 신호 남김
     ↓
  FileSensor: 그 파티션(또는 신호)이 나타났는지 계속 확인
     ↓ (나타나면)
  다운스트림: 수집/가공 태스크 실행
  ```

- 증분 로더 패턴은 잡 스케줄링과 쿼리 실행에 따른 오버헤드로 인해 수집 속도가 느린 편

## 변경 데이터 캡쳐 (CDC)

데이터 수집 시 지연 시간이 낮아야 하거나, 물리 삭제를 지원할 자체 기능이 필요한 경우

- 내부 데이터베이스 커밋 로그에서 수정된 모든 레코드를 지속적으로 직접 수집하는 방식
  - 커밋 로그에서 수집한 변화를 스트리밍 브로커나 다른 구성된 출력으로 전송

- 장점
  - UPDATE, DELETE를 잡을 수 있음

  - 낮은 지연 시간, 소스 부하가 낮음


[소스: 로그 스트림/파일/에이전트] → 스트리밍 수집 또는 증분 배치

- 문제
  - 복잡성
    - 서버에서 커밋 로그를 활성화하는 등 운영 팀의 도움이 필요할 수 있음

  - 데이터 범위
    - 클라이언트 프로세스 시작 전 변경 사항은 수집하기 어려움

  - 페이로드
    - CDC는 부가적인 메타데이터도 함께 제공 → 관련 없는 속성을 무시하도록 처리 로직 조정이 필요할 수 있음

  - 데이터 시맨틱
    - CDC 컨슈머에서 수집된 데이터를 정적 데이터로 간주하면 안됨. 이 패턴은 저장 상태의 데이터를 수집
      - CDC 데이터는 ‘사실의 나열’ 이 아니라 ‘**상태를 재구성하기 위한 변경 스트림**’ 으로 간주해야 함
        - 이벤트 로그가 아니라, 계속 갱신되는 상태의 스냅샷이기 때문에 이 데이터 자체를 정적 데이터로 간주하면 안됨. key와 순서로 현재 상태를 계속 재구성해야 함

      - 변경이 발생한 순서대로 적용될 수 있도록 순서 보장이 중요

    - 행의 값은 계속 바뀌는 가변 상태 → CDC 레코드는 그 변경이 일어난 순간의 스냅샷일 뿐, 영구히 확정된 사실이 아님

- 많이 사용되는 오픈 소스: Debezium

- ex. PostgreSQL용 Debezium 카프카 커넥트 구성
  ```json
  {
  	"name": "visits-connector",
  	"config": {
  		"connector.clas": "io.debezium.connector.postgresql.PostgresConnector",
  		"database.hostname": "postgres", "database.port": "5432",
  		"database.user": "postgres", "database.password": "postgres",
  		"database.dbname": "postgres", "database.server.name": "dbserver1", 
  		"schema.include.list": "dedp_schema",
  		"topic.prefix": "dedp"
  	}
  }
  ```

  - 연결 매개변수와 모니터링 작업에 포함할 모든 스키마, 동기화된 각 테이블에 대해 생성된 토픽의 접두사 정의

  - 결과: dedp_schema.events 테이블이 있는 경우, 모든 변경 사항을 dedp.dedp_schema.events 토픽에 기록

- lake-native 형식은 CDC를 더 간단한 방식으로 지원함
  - 델타 레이크: 변경된 레코드를 스트리밍하는 **데이터 변경 피드(CDF)** 기능 내장

  - 델타 레이크에서 CDF 설정
    ```python
    spark_session_builder.config('spark.databricks.delta.properties.defualts.enableChangeDataFeed', 'true')
    spark_session.sql('''
    	CREATE TABLE events (
    		visit_id STRING, event_time TIMESTAMP, user_id STRING, page STRING
    	)
    	TBLPROPERTIES (delta.enableChangeDataFeed = true)''')
    ```

  - 델타 레이크에서 CDF 사용
    ```python
    events = (spark_session.readStream.format('delta')
    	.option('maxFilesPerTrigger', 4)
    	.option('readChangeFeed', 'true')
    	.option('startingVersion', 0)
    	.table('events'))
    query = events.writeStream.format('console').start()
    ```

  - `_change_type`, `_commit_version`, `_commit_timestamp` 필드 추가됨

## 데이터 복제

데이터를 있는 그대로 한 장소에서 다른 장소로 복사하는 것

- 데이터 복제: 동일한 유형의 스토리지 간의 데이터를 이동. 
  - 이상적으로는 데이터베이스의 기본키나 스트리밍 브로커의 이벤트 위치와 같은 모든 메타데이터 속성을 보존하는 것

  - 현실에서는 컴플라이언스 규정으로 인해 입력 데이터를 변경해야 할 때가 많음

- 데이터 적재: 데이터 복제보다 유연

### 패스스루 복제기

- 문제 예시: 개발, 스테이징, 운영 세가지 환경이 있음. 외부 API로부터 참조 데이터셋을 수집하여 운영 환경에 적재하고 있음. 더 나은 개발 경험과 버그 탐지를 위해 다른 두 환경에도 동일한 데이터셋이 포함되길 원함. 외부 API는 멱등성을 갖지 않아 시점에 따라 서로 다른 결과가 반환될 수 있음

- 멱등성이 없고, 환경 간 일관성이 필요 → 패스스루 복제기 패턴이 알맞음

- 고려할 점
  - 단순하게 유지할 것
    - 데이터를 있는 그대로 유지해야 함 → 데이터베이스에서 사용할 수 있는 데이터 복사 명령어에 의존하면 좋음

    - 그런 명령어를 사용할 수 없고, JSON과 같은 텍스트 형식을 위한 프레임워크를 사용해야 할 경우 → JSON I/O API 대신 원시 텍스트 API를 사용하는 것이 좋음

  - 보안과 독립성
    - pull 대신 push 접근 방식으로 복제를 구현해야 함

  - 개인 식별 정보 데이터
    - 복제된 데이터셋에 PII나 운영 환경에서 전파할 수 없는 종류의 정보가 저장되어있다면 *변환 복제기 패턴*을 사용해야 함 → 예기치 않은 속성 제거

  - 메타데이터
    - 메타데이터를 무시하지 않는 것이 좋음

    - 예를 들어, 델타 레이크 테이블의 parquet 파일만 복제하면 데이터셋이 무용지물이 될 수 있음

- 활용
  - spark를 이용한 JSON 데이터 복제
    ```python
    input_dataset = spark_session.read.text(f'{base_dir}/input/date=2026-07-01')
    input_dataset.write.mode('overwrite').text(f'{base_dir}/output-raw/date=2026-07-01')
    ```

  - 파티션 내 추가적인 순서 보장이 필요한 kafka topic에 대한 추출 및 적재
    ```python
    events_to_replicate = (input_data_stream
    	.selectExpr('key', 'value', 'partition', 'headers', 'offset'))
    	
    def write_sorted_events(events: DataFrame, batch_number: int):
    	(events.**sortWithinPartitions**('offset', ascending=True)
    		.drop('offset')
    		.write.format('kafka')
    		.option('kafka.bootstrap.servers', 'localhost:9094')
    		.option('topic', 'events-replicated')
    		**.option('includeHeaders', 'true)**
    		.save()
    	)
    	
    write_data_stream = (events_to_replicate.writeStream
    	.option(checkpointLocation', f'{get_base_dir()}/checkpoint-kafka-replicator')
    	.foreachBatch(write_sorted_events))
    ```

    - `sortWithinPartitions` : 복제된 레코드가 입력 레코드와 동일한 순서 유지

    - `includeHeaders=true` : 복제된 레코드가 메타데이터 포함

  - terraform을 활용한 S3 버킷 복제
    ```hcl
    resource "aws_s3_bucket_replication_configuration" "replication" {
    	role = aws_iam_role.replication.arn
    	bucket = aws_s3_bucket.devices_production.id
    	
    	rule {
    		id = "devices"
    		status = "Enabled"
    		destination {
    			bucket = aws_s3_bucket.devices_staging.arn
    			storage_class = "STANDARD"
    		}
    	}
    }
    ```

### 변환 복제기

- 예시 상황: 데이터 처리 잡 릴리스하기 전에 실제 데이터로 테스트를 수행하고자 함. 데이터 제공업체에서 일관된 데이터를 제공하지 않기 때문에 운영 환경 데이터를 스테이징 데이터로 복제해야 함. 운영 환경 데이터에는 PII 데이터가 포함되어 있음 → 단순한 패스스루 복제기 사용할 수 없음

- 변환
  - 구현
    - spark, flink 같은 데이터 처리 프레임워크를 사용할 때 사용자 정의 매핑 함수 사용

    - SQL SELECT 문

  - 복제되지 않아야 하는 속성을 익명화 패턴 등으로 대체하거나, 처리에 필요하지 않은 경우 제거

- 문제
  - 텍스트 파일 형식의 변환 위험
    - 날짜 시간 형식 등이 표준과 달라질 수 있음 → ‘단순하게 유지!’ 타임스탬프 컬럼을 그대로 정의하는 대신, 문자열로 간단히 설정

  - 비동기화
    - 현재 보유하고 있는 개인 정보 필드가 미래에도 여전히 유효하리라는 보장이 없음
      - 데이터 카탈로그나 민감한 필드가 태그된 데이터 계약같은 데이터 거버넌스 도구가 필요함 → 변환 로직 자동화 가능

  

- 구현
  - 데이터 축소: 불필요한 필드 제거
    ```sql
    -- Databricks, BigQuery 등 EXCEPT을 지원하는 경우
    SELECT * EXCEPT (ip, latitude, longitude)
    ```

    ```python
    # spark: drop 활용
    input_delta_dataset = spark_session.read.format('delta').load(users_table_path)
    users_no_pii = input_delta_dataset.drop('ip', 'latitude', 'longitude')
    ```

    ```sql
    -- AWS Redshift: 테이블에 대한 컬럼 수준 접근 제한
    GRANT SELECT (visit_id, event_time, user_id) ON TABLE visits TO user_a
    ```

  - 컬럼 기반 변환
    ```python
    devices_trunc_full_name = (input_delta_dataset
    	.withColumn('full_name', 
    		functions.expr('SUBSTRING(full_name, 2, LENGTH(full_name))'))
    )
    ```

    ```scala
    // 매핑 함수 활용: Scala API (python API보다 간결)
    case class Device(`type`: String, full_name: String, version: String) {
    	lazy val transformed = {
    		if (version.startsWith("1.")) {
    			this.copy(full_name = full_name.substring(1), version = "invalid")
    		} else {
    			this
    		}
    	}
    }
    inputDataset.as[Device].map(device => device.transformed()
    ```

    - 매핑 함수: 레코드 수준에서 작업해야 하거나 수정 규칙이 복잡한 경우 사용

## 데이터 컴팩션

점차 데이터셋의 규모가 커지면 병목 현상이 일어날 수 있음

### 컴팩터 패턴

- 기본 파일의 스토리지 용량 줄이기 위한 작업

- 작은 데이터 파일들을 읽어서 같은 레코드를 큰 파일로 다시 써냄 → 물리적으로 데이터 재생성 → 그 후 메타데이터 갱신

- 예시 상황: 실시간 데이터 수집 파이프라인이 스트리밍 브로커에서 객체 스토어로 이벤트 동기화. 단순한 패스스루 잡. 석 달 후, 데이터셋을 구성하는 너무 많은 작은 파일 때문에 메타데이터 오버헤드 문제를 겪고 있음. 결과적으로 실행 시간의 70%가 처리할 파일의 나열에 사용되고, 데이터 처리에는 겨우 30%가 사용됨. → 심각한 시간 지연과 비용에 영향
  - ‘작은 파일 문제’: 객체 스토어(S3/GCS 등)나 쿼리 엔진이 데이터를 처리하려면 실제 내용을 읽기 전에 먼저 어떤 파일들을 읽어야 하는지 목록을 만드는 단계를 거침. 이 나열 비용은 파일 개수에 비례함. 
    - 파일마다 open, 메타데이터/푸터 읽기, 커넥션 셋업

  - 실시간 스트리밍 → 객체 스토어 패스스루
    - 실시간성을 위해 자주 flush → 그때마다 이벤트 몇 개짜리 작은 파일 1개가 생김

    - 객체 스토어는 기존 객체에 append가 안됨. 각 마이크로배치가 무조건 새 파일이 됨

    - 이게 석 달간 쌓이면 작은 파일 수백만 개 → 메타데이터 오버헤드 폭발

    - parquet같은 컬럼 포맷이면 손해가 더 큼. row group이 작아서 압축률, 인코딩 효율, 데이터 스킵이 다 나빠짐. 큰 파일일수록 이런 최적화가 잘 먹힘.

- 구현
  - 오픈 테이블 파일 형식: 전용 컴팩션 명령으로 트랜잭션 분산 데이터 처리 잡 실행 → 새 커밋으로 작은 파일을 큰 파일로 병합

  - Iceberg: 데이터 파일 다시 쓰기 작업을 통해 수행

  - Delta Lake: `OPTIMIZE` 명령 실행

  - Apache Hudi: 데이터셋이 컬럼 형식으로 쓰이고, 이후의 변경 사항은 레코드 형식으로 쓰이는 병합조회 테이블로 설정

  - Kafka: 
    - Kafka와 같은 구성 기반 구현에서는 컴팩션 빈도만 설정하면 됨. 이후 데이터 스토어가 빈도에 따라 전체 컴팩션 프로세스를 관리함.

    - Kafka와 같은 키 기반 시스템에서는 컴팩션이 주어진 레코드 키에 대해 최신의 항목만 유지하는 방식으로 저장 공간 최적화

- 문제
  - 비용 vs. 성능 트레이드오프: 컴팩션 잡은 하루에 한 번 정도, 근무 시간 외에, 데이터셋을 생성하는 파이프라인 외부에서 드물게 실행되어야 함. 반면, 아직 컴팩션 되지 않은 데이터에서 잡이 실행되면 최적화 기술을 사용하지 못해 문제가 될 수 있음. 
    - 비용과 성능 관점에서 어떤 전략이든 완벽하지 않을 수 있음을 받아들여야 함

    - 컴팩션되지 않은 데이터셋이 작아서 하루에 한 번만 잡 실행 / 수집 처리량에 미치는 영향보다 컨슈머에게 주는 피해가 더 커서 데이터 수집 과정에서 컴팩션

  - 일관성
    - 컴팩션은 이미 존재하는 데이터를 다시 쓰는 것. 컨슈머는 사용할 데이터와 컴팩션 중인 데이터를 구별하기 어려울 수 있음

    - 컴펙션은 delta lake, iceberg와 같이 ACID 속성을 가진 현대적인 개방형 테이블 파일 형식에서 훨씬 간단하고 안전함
      - 어떤 파일들이 현재 유효한 테이블 버전인지를 정의하는 메타데이터 (스냅샷/커밋 로그) 계층이 있음

      - 컨슈머는 파일을 나열하는게 아니라 특정 스냅샷을 읽음 → 커밋된 파일 집합만 확인 가능

      - 컴팩션은 하나의 트랜잭션으로 처리됨

  - 정리
    - 컴팩션 잡은 원천 파일을 보존할 수 있음 → 작은 파일이 여전히 존재하며 메타데이터 작업에 계속 영향을 미침

    - 컴팩션 잡만으로는 충분하지 않고, 정리 잡을 완성해야 함

    - delta lake, iceberg, postgresql, redshift와 같은 현대적인 데이터 스토리지 기술에서는 `VACUUM` 명령어 사용

- 예시
  - delta lake를 사용한 컴팩션 잡
    ```python
    devices_table = DeltaTable.forPath(spark_session, table_dir)
    devices_table.optimize().executeCompaction()
    ```

  - 정리 과정: 설정된 보존 임계치보다 오래된 파일에 대해서만 적용됨
    ```python
    devices_table = DeltaTable.forPath(spark_session, table_dir)
    devices_table.vacuum()
    ```

## 데이터 준비

### 준비 마커 패턴

- 가장 적절한 시점에 수집 과정을 시작하는 데 유용한 패턴
  - 목표: 데이터셋의 완전성을 보장하도록 데이터를 수집하는 것

- 예시 상황: 배치 잡을 실행하여 매시간 메달리온 데이터 아키텍처의 실버 계층에서 데이터 준비. 추가 컨텍스트 적용됨. 다른 팀들이 이를 활용해 ML 모델과 BI 대시보드 생성. → 사용하는 팀들이 데이터셋이 불완전하다며, 데이터 소비가 가능한 시점을 알려주는 메커니즘을 구현해달라고 요청
  - 워크로드가 분리된 상황에서는 잡이 직접적으로 다운스트림 파이프라인을 트리거할 수 없음 → 준비 마커 패턴을 사용해 데이터셋을 처리 준비 상태로 표시할 수 있음

- 구현
  - **플래그 파일** 로 구현
    - spark, delta lake의 새로운 커밋 로그와 같이 데이터 처리 계층에서 기본적으로 사용 가능

    - 데이터 처리 계층을 활용할 수 없다면, 데이터 오케스트레이션 계층에서 별개의 작업으로 플래그 파일을 생성하도록 구현할 수 있음

  - 파티션된 데이터 원천
    - 시간 기반 테이블이나 위치에 대한 데이터를 생성하는 경우, 굳이 완료 마커 파일을 만들지 않고, “다음 파티션이 생기면 이전 파티션은 완료된 것”이라는 관례를 쓸 수 있음

- 문제
  - 강제성 부족: 컨슈머에게 준비 규칙을 따르는 것을 강제할 수는 없음

  - 지연 데이터에 대한 신뢰성
    - 파티션 기반 구현 시 데이터 지연 문제를 겪을 수 있음. 이미 닫힌 파티션에 뒤늦게 지연 데이터가 발생할 수 있음
      - 파티션을 한 번 닫히면 절대 변하지 않을 불변의 영역으로 간주하거나 변경 조건을 명확히 정의하고 컨슈머와 공유해야 함

- 예시
  - spark: `_SUCCESS` 파일 생성
    ```python
    dataset = (spark_session.read.schema('...').json(f'{base_dir}/input')
    dataset.write.mode('overwrite').format('parquet').save('devices-parquet')
    ```

  - airflow: `FileSensor` 조건으로 정의
    ```python
    FileSensor(filepath=f'{input_file_path}/_SUCCESS', mode='reschedule' ...)
    ```

  - airflow에서 준비 마커 파일 생성
    ```python
    @task
    def delete_dataset():
    	shutil.rmtree(dataset_dir, ignore_errors=True)
    	
    @task
    def generate_dataset():
    	# processing
    	
    @task
    def create_readiness_file():
    	with open(f'{dataset_dir}/COMPLETED', 'w') as marker_file:
    		marker_file.write('')
    		
    delete_dataset() >> generate_dataset() >> created_readiness_file()
    ```

## 이벤트 주도

데이터가 들어오는 빈도를 예측하기 어려운 경우 → 이벤트 기반 수집으로 전환

### 외부 트리거 패턴

- 데이터 가용성에 대해 컨슈머에게 알리는 일을 프로듀서가 수행: **푸시 시맨틱**

- 예시 상황: 새롭게 처리할 기능이 있을 때에만 파이프라인을 실행하고자 함. 새 기능을 게시할 때마다 중앙 메시징 버스로 알림 이벤트가 전송됨.

- 구현
  1. **알림 채널 구독하기**

  2. **알림에 반응하기** (이벤트 핸들러): 이벤트 분석 → 데이터 오케스트레이션 계층/데이터 처리 계층 중 어디에서 잡을 시작할지 결정

  3. **데이터 오케스트레이션/데이터 처리 계층에서 데이터 수집 파이프라인 트리거하기**: 하나의 이벤트는 하나의 수집 파이프라인을 트리거해야 함. 물론 동일한 데이터셋이 여러 작업의 입력 데이터 원천인 경우 여러 개를 시작하는 것도 가능

- 문제
  - 실행 컨텍스트: 외부 트리거가 단순히 엔드포인트를 호출하는 핑 메커니즘이 될 위험이 있음 → 왜 트리거가 되었는지, 무엇을 처리해야 하는지에 대한 충분한 컨텍스트가 없을 수 있음
    - 메터 데이터 정보로 트리거 잡의 버전, 알림 envelope, 처리에 걸린 시간, 이벤트 시간 등이 포함되어야 함

  - 오류 관리: 어떤 상황에서든 이벤트가 유지되는 것을 목표로 해야 함. (ex. 데드 레터 패턴 등)

- 예시
  - Airflow DAG를 트리거하는 람다 핸들러
    ```python
    def lambda_handler(event, ctx):
    	payload = {
    		'event': json.dumps(event),
    		'trigger': {
    			'function_name': ctx.function_name,
    			'function_version': ctx.function_version,
    			'lambda_request_id': ctx.aws_request_id
    		},
    		'file_to_load': (urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')),
    		'dag_run_id': f'External-{ctx.aws_request_id}'
    	}
    	
    	trigger_Response = requests.post('http://localhost:8000/api/v1/dags/devices-loader/dagRuns', data=json.dumps({'conf': payload}), auth=('dedp', 'dedp'), headers=headers)
    	
    	if trigger_response.status_code != 200:
    		raise Exception(f"""Couldn't trigger the `devices-loader` DAG. {trigger_response} for {payload}""")
    		
    	else:
    		return True
    ```