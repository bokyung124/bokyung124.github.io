---
title: "Airflow Celery Executor"
last_modified_at: 2025-10-14T02:39:00+00:00
notion_page_id: 28812b31-a8a8-8036-b492-de3f1afe9166
layout: post
categories:
    - Data Engineering
excerpt: ""
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [Data Engineering]
---

![image](/assets/img/image.png)

출처: [https://medium.com/sicara/using-airflow-with-celery-workers-54cb5212d405](https://medium.com/sicara/using-airflow-with-celery-workers-54cb5212d405)



## Celery Executor 아키텍처

1. **웹서버**

1. **스케줄러**

1. **메타데이터 데이터베이스**

1. **메시지 브로커**

1. **Celery Workers**

1. **Result Backend**



**데이터 흐름 요약:**

스케줄러 → (Task 메시지) → 메시지 브로커 (Queue) → (Task 메시지) → Celery 워커 → (Task 실행) → 결과 백엔드 → (상태 업데이트) → 메타데이터 DB



## Celery Executor 구축 과정

### GCP Infra

- VM 머신: Compute Engine



- 메타데이터 데이터베이스: Cloud SQL



- 메시지 브로커: Redis



- 로깅: Cloud Storage에 별도 저장



- 클라우드 인프라 구성은 terraform을 이용했습니다.



### VM 환경 구성

1. **Python**

1. **Airflow**

1. **AIRFLOW_HOME**

1. **Redis**



### Airflow 설정

- AIRFLOW_HOME으로 이동하여 `airflow db init` 을 수행하면, airflow.cfg 파일이 생성됩니다.

- 해당 파일을 수정하여 설정을 변경합니다.



1. **database 설정**

```bash
[database]
sql_alchemy_conn = postgresql+psycopg2://{username}:{password}@{cloud_sql_ip}/{database}
```



1. **core 설정**

```bash
[core]
executor = CeleryExecutor

load_examples = False
```



1. **logging 설정**

```bash
[logging]
base_log_folder = {$AIRFLOW_HOME}/logs

remote_logging = True

delete_local_logs = True

remote_log_conn_id = {gcs_connection_id}

remote_log_folder = gs://{gcs_bucket_name}/logs

log_filename_template = {{ ti.dag_id }}/{{ ti.task_id }}/{{ ts }}/{{ ti.try_number }}.log

log_format = %%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s

simple_log_format = %%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s
```

- 외부 버킷에 로그를 저장하기 위해서** base_log_folder, remote_logging, delete_local_logs, remote_log_conn_id, remote_log_folder** 설정이 필요합니다.

- base_log_folder (로컬 VM 머신) 에 먼저 로그를 쌓은 뒤, Task가 종료되면 remote_log_folder로 로그를 복사하고 로컬의 로그를 삭제합니다.



1. **api 설정**

```bash
auth_backends = airflow.api.auth.backend.session
```

- 웹 서버에 접근할 때 사용하는 인증 방식을 **기본 인증**으로 지정합니다. (아이디, 비밀번호)

- 비밀번호가 암호화되지 않기 때문에 HTTPS와 함께 사용해야 합니다.



1. **webserver 설정**

```bash
[webserver]
workers = 2

default_ui_timezone = Asia/Seoul

base_url = https://{domain}

rate_limit_storage_uri = redis://{password}@localhost:6379/1
```

- `rate_limit_storage_uri` 설정은 웹서버의 요청 횟수 제한 상태를 저장할 저장소 주소를 지정합니다. 주로 Redis를 사용합니다. 



1. **scheduler 설정**

```bash
[scheduler]
enable_health_check = True
```



1. **celery 설정**

```bash
[celery]
broker_url = redis://{password}@localhost:6379/0
result_backend = redis://{password}@localhost:6379/2

worker_prefetch_multiplier = 1
task_acks_late = True
task_track_started = True
task_send_sent_event = True
task_soft_time_limit = 3600
task_time_limit = 3600

worker_concurrency = 4
```

- `broker_url` 설정은 메시지 브로커의 주소입니다. 로컬에 설치된 Redis의 0번 DB를 사용합니다.

- `result_backend` 설정은 result backend 를 저장할 DB 주소입니다. Redis의 2번 DB를 사용합니다.



- `task_acks_late` 설정은 워커가 Task를 언제 ‘처리 완료’ 로 간주할지 결정하는 옵션입니다. 

- `task_soft_time_limit` , `task_time_limit` 설정은 특정 Task가 비정상적으로 오래 실행되어 시스템 전체에 영향을 주는 것을 방지하는 Timeout 설정입니다.



- `task_track_started` 를 True로 설정하면 Task가 “실행 시작” 상태일 때, 그 상태를 결과 백엔드에 기록합니다. Airflow UI에서 Task 상태가 ‘queued’ → ‘success’ 로 바뀌는 것이 아니라, ‘queued’ → **’running’** → ‘success’ 로 바뀌어 더욱 상세한 모니터링이 가능합니다.

- `task_send_sent_event` 는 스케줄러가 워커에서 Task를 성공적으로 보냈을 때 ‘sent’ 이벤트를 발생시킬지 여부를 결정합니다. Flower와 같은 Celery 모니터링 도구에서 주로 사용되어 Task의 전체 생명주기를 더 정확하게 추적하고 시각화해줍니다.



- `worker_prefetch_multiplier` 는 워커가 자신의 동시성 (concurrency)에 기반하여 한 번에 몇 개의 Task를 미리 가져올지 결정하는 배수입니다.

- `worker_concurrency` 는 단일 Celery 워커 프로세스가 동시에 실행할 수 있는 Task의 최대 개수를 지정합니다. 이 값은 워커가 실행되는 서버의 CPU 코어 수와 메모리, Task의 리소스 사용량을 고려하여 설정합니다.



## Airflow 사용자 생성

```bash
GENERATED_PASSWORD=$(openssl rand -base64 12)
echo "Generated password: $GENERATED_PASSWORD"

# 생성된 비밀번호로 사용자 생성
airflow users create \
    --username {username} \
    --firstname {firstname} \
    --lastname {lastname} \
    --role Admin \
    --email {email} \
    --password "$GENERATED_PASSWORD"
    
# 사용자 비밀번호 변경
airflow users reset-password \
    --username dev \
    --password {new_password}
```



## Systemd Service 생성

systemd service로 airflow를 구성하여 쉽고 안정적으로 서비스를 운영합니다.



### airflow-worker@.service

```bash
[Unit]
Description=Airflow Celery Worker %i
After=network.target postgresql.service redis-server.service
Wants=redis-server.service
Documentation=https://airflow.apache.org/docs/

[Service]
User={username}
Group={group}
Type=simple
EnvironmentFile={$AIRFLOW_HOME}/environment

# 'airflow' 래퍼 대신 'celery' 직접 실행하여 Worker 별 hostname 지정
ExecStart=/home/{username}/.pyenv/versions/.venv/bin/celery -A airflow.providers.celery.executors.celery_executor.app worker --loglevel INFO -E --hostname 'worker%i@%H' --queues default

Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

- 하나의 VM 머신에서 여러 워커 프로세스를 실행하려면 airflow wrapper 대신 celery로 직접 실행해야합니다. 

- 워커 프로세스 노드 이름이 고유해야 하는데, airflow wrapper는 `%i` 와 같은 템플릿 변수를 제대로 파싱할 수 없기 때문에 고유한 노드 이름이 생성되지 않습니다.



### airflow-webserver.service

```bash
[Unit]
Description=Airflow Webserver Daemon
After=network.target postgresql.service redis-server.service
Documentation=https://airflow.apache.org/docs/

[Service]
User={username}
Group={group}
Type=simple
EnvironmentFile={$AIRFLOW_HOME}/environment
ExecStart=/home/{username}/.pyenv/versions/.venv/bin/airflow webserver --port 80
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```



### airflow-scheduler.service

```bash
[Unit]
Description=Airflow Scheduler Daemon
After=network.target postgresql.service redis-server.service
Documentation=https://airflow.apache.org/docs/

[Service]
User={username}
Group={group}
Type=simple
EnvironmentFile={$AIRFLOW_HOME}/environment
ExecStart=/home/{username}/.pyenv/versions/.venv/bin/airflow scheduler
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```



### airflow-flower.service

```bash
[Unit]
Description=Airflow Celery Flower
After=network.target redis-server.service

[Service]
User={username}
Group={group}
Type=simple
EnvironmentFile={$AIRFLOW_HOME}/environment
ExecStart=/home/{username}/.pyenv/versions/.venv/bin/airflow celery flower --port=5555 --host=0.0.0.0
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```



### service 시작

```bash
sudo systemctl daemon-reload

sudo systemctl enable airflow-worker@{1,2} airflow-worker airflow-scheduler airflow-flower

sudo systemctl start airflow-worker@{1,2} airflow-worker airflow-scheduler airflow-flower

sudo systemctl status 'airflow-worker@*.service'
```



## DAG 배포 자동화

- 배포 자동화는 GCP Cloud Build를 사용합니다.

- main 브랜치에 push가 되면 `git pull origin main` → airflow service들을 모두 재시작합니다.

- Cloud Build에서 VM 인스턴스에 접근하기 위해 Worker Pool과 SSH Key를 사용했습니다.
