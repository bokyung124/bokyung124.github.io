---
title: "[책] 데이터 엔지니어링 디자인 패턴 - 오류 관리 디자인 패턴"
last_modified_at: 2026-07-11T16:52:00+00:00
notion_page_id: 39a12b31-a8a8-801e-bf42-d9e2f32021a4
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

# 오류 관리 디자인 패턴

## 데드 레터 패턴

- 잘못된 레코드를 무시하고 올바른 레코드를 계속 처리

- 잘못된 레코드를 다른 곳에 저장하여 추가 조사 수행

### 해결

1. 잡이 실패할 수 있는 코드 위치 식별

2. 식별된 실패 가능 지점에 안전 제어 추가
  1. `try-catch` / `if-else`

  2. 사후 분석에서 실패를 잘 이해할 수 있도록 실패한 메시지를 메타데이터에 포함

3. 오류가 있는 이벤트를 위해 다른 출력 구성
  1. 클라우드의 객체 스토어 / 스트리밍 브로커가 적합
    1. 복원성, 모니터링 용이성, 쓰기 성능

4. 실패한 레코드를 메인 데이터 흐름으로 수집하는 리플레이 파이프라인 (과거 데이터가 필요한 경우)

### 문제

- 스노우볼 백필링 효과
  - 리플레이 파이프라인 실행 → 수집된 레코드가 다운스트림 컨슈머에 의해 이미 처리된 파티션에 들어갈 수 있음 → 백필링 작업 필요 + 모든 다운스트림 컨슈머도 데이터를 다시 처리해야 함

- 데드 레터 레코드 식별
  - 데드 레터 레코드를 메인 데이터 스토어에 통합하지만, 정상적인 데이터 수집 파이프라인에서 추가된 레코드와 구별하고 싶을 수 있음
    - `was_dead_lettered` 속성이나 불리언 컬럼 추가

    - 메타데이터를 사용하여 잡 이름, 버전, 리플레이 시간을 레코드에 주석으로 추가 (데이터 데코레이터 패턴)

- 순서와 일관성 문제

- 오류-안전 함수를 사용할 경우 오류가 발생하면 런타임 에러를 던지지 않고 NULL 값 반환 → 데드 레터 패턴 구현이 어려워짐
  - 예외 포착 대신, 출력값을 입력값과 비교해야 함

### 예제

- 오류 레코드가 있어도 파이프라인이 실행될 수 있기 때문에 스트림 처리 컨텍스트에서 자주 인용됨

- flink: 사이드 출력 기능 의존
  ```python
  # Flink의 데드 레터 컴포넌트
  invalid_data_output: OutputTag = OutputTag('invalid_visits', Types.STRING())
  visits: DataStream = data_source.map(MapJsonToReucedVisit(invalid_data_output), Types.STRING())
  ```

  ```python
  # Flink에서 사이드 출력 쓰기와 조회
  def map_rows(self, json_payload: str) -> str:
  	try:
  		evt = json.loads(json_payload)
  		evt_time = int(datetime.datetime.fromisoformat(evt['event_time'])
  		yield json.dumps({'visit_id': evt['visit_id'], 'event_time': evt_time, 'page': evt['page']})
  	except Exception as e:
  		yield self.invalid_data_output, _wrap_input_with_error(json_payload, e)
  		
  kafka_sink_valid_data: KafkaSink = ...
  kafka_sink_invalid_data: KafkaSink = ...
  
  visits.get_side_output(invalid_data_output).sink_to(kafka_sink_invalid_data)
  visits.sink_to(kafka_sink_valid_data)
  ```

- 오류-안전 변환을 위한 데드 레터 패턴: 쿼리
  ```python
  spark_session.sql('''
  	SELECT type, full_name, version, name_with_version,
  		WHEN (full_name IS NOT NULL OR version IS NOT NULL)
  			AND name_with_version IS NULL THEN false ELSE true
  		END AS is_valid
  	FROM (SELECT type, full_name, version, CONCAT(full_name, version) AS name_with_version FROM devices_to_load)
  	''')
  ```

  - `CONCAT`: 오류-안전 변환. 결합된 컬럼 중 하나가 null이면 null을 반환함.

- 오류-안전 변환을 위한 데드 레터 패턴: 기록
  ```python
  devices_to_load_with_validity_flag.persist()
  
  (devices_to_load_with_validity_flag.filter('is_valid IS TRUE')
  	.drop('is_valid')
  	.write.mode('overwrite')
  	.format('delta')
  	.save(f'{base_dir}/output/devices-table'))
  	
  (devices_to_load_with_validity_flag.filter('is_valid IS FALSE')
  	.drop('is_valid')
  	.write.mode('overwrite')
  	.format('delta')
  	.save(f'{base_dir}/output/devices-dead-letter-table')
  ```

  - `.persist()` : 쿼리가 두 번 실행되는 것 방지

## 중복된 레코드

### 윈도 중복 제거 패턴

- 스트리밍 잡: 시간 기반 윈도로 제한 범위 설정

- 배치 잡: 현재 처리 중인 데이터셋으로 범위 한정

### 해결책

- 배치 잡: `row_number()` + `DISTINCT` or `WINDOW Function`

- 스트리밍 잡: 과거의 어떤 상태를 저장하는 *상태 스토어* 활용
  - 로컬: 상태 데이터는 메모리에 존재. 가장 빠른 해결책이지만, 운영 환경에서 실패가 발생했을 때 상태 손실

  - 내결함성을 갖춘 로컬: 상태는 주로 메모리에 존재, 추가적으로 원격 스토리지에 저장 → 시간/일관성 측면에서 비용 발생

  - 원격: 상태는 원격 데이터 스토어에만 존재. 데이터 지연, 파이프라인의 전체적인 비용 발생

### 결과

- 완벽한 중복 제거를 보장하진 못함

- 공간 vs. 시간 트레이드오프 (스트리밍 파이프라인)
  - 스트리밍 파이프라인은 장시간 실행되기 때문에 시간 기반의 중복 제거 윈도를 사용하며, 지정된 기간 내에서만 중복 데이터를 찾음

  - 짧은 윈도는 중복된 데이터 일부를 놓칠 수 있지만, 자원에 미치는 영향은 작을 것

  - 윈도를 늘리면 더 많은 고유 키를 상태 스토어에 저장하고 관리해야 하므로 더 많은 자원이 필요

- 멱등성 프로듀서
  - 정확하게 중복 데이터를 제거했더라도 처리된 레코드가 정확히 한 번만 전달된다는 보장은 없음

### 예제

- spark: `dropDuplicates` 함수 제공
  ```python
  dataset = (session.read.schema('...').format('json').load(f'{base_dir}/input'))
  deduplicated = dataset.dropDuplicates(['type', 'full_name', 'version'])
  ```

- 네이티브 중복 제거가 없는 경우 → `WINDOW 함수` 사용
  - 모든 레코드를 그룹화하고 첫번째 위치를 제외한 모든 것을 필터링

  ```sql
  SELECT type, full_name, version FROM (
  	SELECT type, full_name, version,
  		ROW_NUMBER() OVER (PARTITION BY type, full_name, version ORDER BY 1) AS position
  	FROM duplicated_devices
  ) WHERE position = 1
  ```

- spark streaming: `dropDuplicates` 를 이용한 중복 제거
  ```python
  event_schema = StructType([StructField("visit_id", StringType()), StructField("visit_time", TimestampType())])
  deduplicated_visits = (input
  	.select(F.from_json("value", event_schema).alias("value_struct"), "value")
  	.select("value_struct.visit_time", "value_struct.visit_id", "value")
  	.withWatermark("visit_time", "10 minutes")
  	.dropDuplicates(["visit_id", "visit_time"])
  	.drop("visit_time", "visit_id")
  ```

  - 잡이 조회한 레코드를 얼마나 오래 기억할지 설정해야 함: `watermark`
    - 워터마크보다 오래된 모든 기억된 엔트리는 자동으로 제거됨

## 지연 데이터

### 지연 데이터 탐지기

- 어떤 데이터가 지연되었는지 감지 → 지연 데이터를 누락시키지 않고 탐지 가능한 신호로 만들어 대응하기 위함

- 이벤트 시간: 이벤트가 실제로 발생한 시각

- 처리 시간: 데이터 파이프라인이 해당 작업과 상호 작용한 시점

### 워터마크

- 지연의 판정 기준

- 이 시점 이전의 데이터는 다 도착했다고 간주

- **허용 지연치**: 예상 밖의 지연을 허용하기 위함. 
  - 지연 데이터 탐지기 패턴은 워크플로의 추적된 이벤트 시간에서 허용된 지연 시간 값을 뺀 결과를 워터마크로 결정

### 구현

1. 기준선 유지: 워터마크 계속 추적

2. 비교: 들어오는 각 레코드의 이벤트 시간을 워터마크와 비교

3. 판정: 워터마크보다 과거이면 지연 데이터로 표시

4. 분리: 지연 레코드를 정상 흐름과 다른 경로로 보냄

### 예제

지연 데이터 탐지기 패턴은 주로 **스트림 처리**에 존재

- spark: `withWatermark`
  - 매개변수 1: 시간 추적을 위한 이벤트 시간 속성

  - 매개변수 2: 허용되는 지연 시간

  - spark 구조적 스트리밍은 모든 지연 데이터를 대신 처리함 → 지연 레코드 포착이 어려움

  ```python
  visits_events = (input_data.selectExpr('CAST(value AS STRING)')
  	.select(F.from_json('value', 'visit_id INT, event_time TIMESTAMP, page STRING').alias('visit')).selectExpr('visit.*'))
  	
  session_window: DataFrame = (visit_events
  	.withWatermark('event_time', '1 hour')
  	.groupBy(F.window(F.col('event_time'), '10 minutes')).count())
  ```

  ![image](/assets/img/image.png)

  - 워터마크: 허용 지연치 (1시간) 만큼 뒤처짐

  - 윈도: 워터마크가 자기 끝을 넘어설 때 (워터마크가 갱신될 때) 방출됨

- flink: 실행 컨텍스트에서 현재 워터마크 값에 접근할 수 있음
  1. 수신 단계에서 이벤트 시간 값을 추출할 타임스탬프 할당자 인스턴스 생성

  2. 워터마크를 인식하는 데이터 프로세서 함수 선언

  ```python
  class VisitTimestampAssigner(TimestampAssigner):
  	# 이벤트 시간 알려줌
  	def extract_timestamp(self, value: Any, record_timestamp: int) -> int:
  		event = json.loads(value)
  		event_time = datetime.datetime.fromisoformat(event['event_time'])
  		return int(event_time.timestamp())
  
  class VisitLateDataProcessor(ProcessFunction):
  	
  	def __init__(self, late_data_output: OutputTag):
  		self.late_data_output = late_data_output
  		
  	def process_element(self, value: Visit, ctx: 'ProcessFunction.Context'):
  		current_watermark = ctx.timer_service().current_watermark()
  		if current_watermark > value.event_time:
  			# 지연 데이터 판정 -> side output으로 보냄
  			yield (self.late_data_output, json.dumps(VisitWithStatus(visit=value, is_late=True).to_dict())
  		else:
  			# 정상 -> 메인 출력으로 보냄
  			yield json.dumps(VisitWithStatus(visit=value, is_late=False).to_dict())
  ```

  이후 데이터 처리 잡과 통합해야 함

  ```python
  watermark_strategy = (WatermarkStrategy
  	.for_bounded_out_of_orderness(Duration.of_seconds(5))
  	.with_timestamp_assigner(VisitTimestampAssigner())
  
  data_source = env.from_source(source=kafka_source,
  	watermark_strategy=watermark_strategy, source_name="Kafka Source").uid("Kafka Source").assign_timestamps_and_watermarks(watermark_strategy)
  	
  late_data_output: OutputTag = OutputTag('late_events', Types.STRING())
  visits: DataStream = (data_source.map(map_json_to_visit)
  	.process(VisitLateDataProcessor(late_data_output), Types.STRING()))
  	
  kafka_sink_valid_data: KafkaSink = ...
  kafka_sink_invalid_data: KafkaSink = ...
  
  visits.get_side_output(late_data_output).sink_to(kafka_sink_late_visits)
  visits.sink_to(kafka_sink_valid_data)
  ```

### 정적 지연 데이터 통합기

- 탐지된 지연 데이터를 이미 저장된 결과 데이터셋에 병합해 넣는 패턴

- 이미 출력되어 저장된 결과 데이터셋을 *정적인 대상*으로 보고, 별도의 작업으로 지연 데이터를 그 위에 병합함

### 동작 흐름

1. 빠른 경로(스트리밍): 파이프라인이 윈도를 제때 닫고 결과를 싱크에 저장. 늦은 데이터를 무한정 기다리지 않기 때문에 상태가 가볍고 지연이 낮음

2. 분리: 지연 데이터 탐지기가 늦게 온 레코드를 별도 저장소 (지연 데이터 테이블)로 빼움

3. 보정 경로(정적 통합기): 별도의 잡이 그 지연 데이터를 읽어서 영향 받은 윈도/파티션이 무엇인지 파악하고, 그 구간을 재계산한 뒤 이미 저장된 결과 테이블에 병합하거나 덮어씀

### 전제 조건

- 결과 싱크가 갱신을 지원해야 함 (delta lake, iceberg 등 ACID 속성을 가진 테이블 포맷이 잘 맞음)

- 통합은 멱등이어야 함

### 문제

- 스노우볼 백필링 효과: 컨슈머가 있다면 컨슈머들도 이 파티션에 대한 백필링을 실행해야 함

- 중첩 실행 및 백필링: 룩백 윈도가 존재하기 때문에 여러 구간을 백필하면 실행하는 윈도가 겹칠 수 있음

- 파이프라인 트리거: 백필링 잡은 메인 파이프라인의 일부가 되어야 함

- 자원 낭비: 룩백 윈도의 고정된 기간은 매번 지연 데이터를 포함하지 않을 수 있음

- 시간 요구 사항: 데이터셋이 시간에 따라 파티션되지 않거나 시간 개념이 없다면 지연 데이터를 감지하고 통합할 수 없음

### 예제

- airflow - 이틀간 정적 윈도로 백필링 태스크 생성
  ```python
  @task
  def generate_backfilling_runs():
  	# 지연 데이터가 있는 날짜들을 찾아 리스트로 반환
  	dr: DagRun = get_current_context()['dag_run']
  	backfilling_dates = []
  	days_to_backfill = 2
  	start_date_to_backfill = (dr.execution_date - datetime.timedelta(days=days_to_backfill))
  	for days_to_add in range(0, days_to_backfill):
  		date_to_backfill = start_date_to_backfill + datetime.timedelta(days=days_to_add)
  		backfilling_dates.append(date_to_backfill.date().strftime('%Y-%m-%d'))
  	return backfilling_dates
  ```

  `expand()` 메서드를 사용한 동적 태스크 매핑 → 각 날짜에 대해 하나의 통합 태스크 생성
  - 동적 태스크 매핑: 앞 태스크의 출력을 받아서 그 원소 개수만큼 태스크 인스턴스를 런타임에 자동 생성

  - 지연 데이터에 영향받은 날짜가 몇 개일지는 매번 다르기 때문에 `expand()`로 그 날짜마다 통합 태스크를 하나씩 동적으로 생성 → 각 태스크가 자기 날짜의 파티션만 재계산, 병합함

  ```python
  # expand 메서드에서 각각의 백필된 날짜에 대한 태스크 생성
  @task
  def integrate_late_data(late_date :str):
  	# 해당 날짜의 파티션을 재계산해서 결과 테이블에 병합 (upsert)
  	copy_file(late_date)
  
  # ...
  integrate_late_data.expand(late_date=generate_backfiilling_runs()) # -> 날짜마다 태스크 1개씩 생성
  ```

### 동적 지연 데이터 통합기

- 지연 데이터의 영향을 받는 파티션만 적재하는 도적인 접근 방식
  - → 각 파티션의 마지막 갱신 시간을 저장할 추가 데이터 구조 필요

  - 파이프라인에서 쿼리를 실행할 곳도 정의해야 함
    - 일반적으로 데이터를 성공적으로 처리한 후 마지막 처리 시간 갱신

### 지연 파티션 목록 가져오는 쿼리

```sql
SELECT partition FROM state_table
WHERE `Last update time` > `Last processed time`
AND `Partition` < `Processed partition`
```

### 마지막 갱신 시간

- BigQuery: 각 파티션의 `last_modified_timestamp` 속성 + `INFORMATION_SCHEMA.PARTITIONS` 뷰 제공