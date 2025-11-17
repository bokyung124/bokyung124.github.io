---
title: "GCP Cloud Build를 활용한 Spring boot 배포 자동화"
last_modified_at: 2025-09-30T08:00:00-05:00
layout: post
categories:
    - GCP
excerpt: 
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [GCP, Cloud Build, Springboot]
---

# GCP Cloud Build로 배포 자동화

Github 레포지토리의 main 브랜치에 push가 발생할 경우 GCP Cloud Build에서 빌드 및 배포까지 실행하는 파이프라인을 만들어보았습니다.



#### Cloud Build&#x20;

1. **GCP Cloud Build > 트리거 > 트리거 만들기**
    1. 이벤트: 브랜치로 푸시
    2. 소스: 2세대
    3. 브랜치: `^main$`
    4. 유형: Cloud Build 구성 파일 (YAML 또는 JSON)
    5. 위치: 저장소
2. **cloudbuild.yaml 배포 과정**
    0. Cloud Build가 트리거될 때 트리거된 소스 코드를 `/workspace` 에 압축 해제해두기 때문에 따로 `git pull`을 할 필요 없음
    1. GCS > {bucket\_name}/credential 폴더에서 credentials.json 파일 복사
    2. `gradle clean build -Pprofile=prod -x test` 빌드 실행
    3. 빌드 파일 실행
        1. GCS > {bucket\_name}/history 폴더에 빌드 파일을 저장하여 버전 관리
    4. 배포 스크립트 (deploy.sh) 실행&#x20;
        1. 그냥 백그라운드로 실행하면 로그 출력 때문에 빌드가 끝나지 않음!
            1. `> $HOME_DIR/nohup.out 2>&1 &` 을 추가하여 로그를 파일에서 관리하고 스크립트는 종료


#### YAML 파일

```yaml
steps:
    # 웹서비스에 필요한 credential 파일 다운로드 (GCP 서비스 계정 키 파일 등)
  - name: 'gcr.io/cloud-builders/gsutil'
    args:
      - 'cp'
      - 'gs://{gcs_bucket_name}/credential/*.json'
      - '/workspace/server/mkt-solution/src/main/resources/'

  - name: 'ubuntu'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "INFO: Listing JSON files in the directory:"
        ls -l /workspace/server/mkt-solution/src/main/resources/
        chmod -R 777 /workspace/server/mkt-solution/src/main/resources/*.json

    # Build
  - name: 'gradle:8.8-jdk17'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd /workspace/server/mkt-solution
        if gradle clean build -Pprofile=prod -x test; then
          echo "Build succeeded."
        else
          echo "Build failed."
          curl -X POST "{slack_webhook_url}" -H "Content-Type: application/json" -d "{\"text\": \"$_BUILD_FAIL\"}"
          exit 1
        fi

    # GCS에 빌드된 jar 파일 적재 (히스토리 관리)
  - name: 'gcr.io/cloud-builders/gsutil'
    args:
      - 'cp'
      - '/workspace/server/mkt-solution/build/libs/mkt-solution-0.0.1-SNAPSHOT.jar'
      - 'gs://{gcs_bucket_name}/history/$BUILD_ID-mkt-solution-0.0.1-SNAPSHOT.jar'

  - name: 'gcr.io/cloud-builders/gsutil'
    args:
      - 'cp'
      - '/workspace/server/mkt-solution/deploy.sh'
      - 'gs://{gcs_bucket_name}/'

    # VM에 접속하여 배포 스크립트 실행
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "INFO: Deploying application"
        curl -X POST "{slack_webhook_url}" -H "Content-Type: application/json" -d "{\"text\": \"$_START\"}"
        
        # Secret Manager에서 SSH 키 가져오기
        mkdir -p /root/.ssh
        gcloud secrets versions access latest --secret="{secret_name}" > /root/.ssh/id_rsa
        chmod 600 /root/.ssh/id_rsa
        
        # 알려진 호스트 추가
        cat > /root/.ssh/config << EOF
        Host *
          StrictHostKeyChecking no
          UserKnownHostsFile=/dev/null
          LogLevel=DEBUG3
        EOF
        
        # SSH 명령 실행
        ssh -i /root/.ssh/id_rsa {vm_username}@{vm_internal_ip} "sudo gsutil cp gs://{gcs_bucket_name}/deploy.sh /home/{vm_username}/ && sudo chmod +x /home/{vm_username}/deploy.sh && sudo /home/{vm_username}/deploy.sh $BUILD_ID"
        
        if [[ $? -eq 0 ]]; then
          curl -X POST "{slack_webhook_url}" -H "Content-Type: application/json" -d "{\"text\": \"$_SUCCESS\"}"
        else
          curl -X POST "{slack_webhook_url}" -H "Content-Type: application/json" -d "{\"text\": \"$_FAIL\"}"
        fi

# 슬랙 메시지 변수로 정의
substitutions:
  _BUILD_FAIL: "❌ Ads Hub build failed. Please check the system and try again.  - <https://github.com/{organization_name}/{repository_name}/commit/${COMMIT_SHA}|Github>, <https://console.cloud.google.com/cloud-build/builds;region=asia-east1/${BUILD_ID}?authuser=2&project={gcp_project_id}|CodeBuild>"
  _START: "🚀 Ads Hub deployment started. Please monitor. - <https://github.com/{organization_name}/{repository_name}/commit/${COMMIT_SHA}|Github>, <https://console.cloud.google.com/cloud-build/builds;region=asia-east1/${BUILD_ID}?authuser=2&project={gcp_project_id}|CodeBuild>"
  _SUCCESS: "✅ Ads Hub deployment completed. Thank you for your patience. - <https://github.com/{organization_name}/{repository_name}/commit/${COMMIT_SHA}|Github>, <https://console.cloud.google.com/cloud-build/builds;region=asia-east1/${BUILD_ID}?authuser=2&project={gcp_project_id}|CodeBuild>"
  _FAIL: "❌ Ads Hub deployment failed. Please check the system and try again.  - <https://github.com/{organization_name}/{repository_name}/commit/${COMMIT_SHA}|Github>, <https://console.cloud.google.com/cloud-build/builds;region=asia-east1/${BUILD_ID}?authuser=2&project={gcp_project_id}|CodeBuild>"

options:
  logging: CLOUD_LOGGING_ONLY
  #  machineType: 'E2_HIGHCPU_8'
  pool:
    name: 'projects/{gcp_project_id}/locations/asia-northeast3/workerPools/{worker_pool_name}'
  dynamicSubstitutions: true
```

* `name`: 실행할 컨테이너 이미지
* `entrypoint`: 컨테이너가 시작될 때 실행할 명령어
* `args`: entrypoint에 전달할 인자들 지정
  * 여러 명령어는 `-c` 플래그로 지정
  * `|` 파이프를 이용하여 여러 줄의 명령어 실행
* `substitutions`: 빌드 과정에서 사용할 변수 정의
* `dynamicSubstitutions`: true로 지정하면 동적으로 변수 값 설정 가능



#### 배포 스크립트

* application.yaml 에 필요한 보안 변수들은 GCP Secret Manager로 관리
* systemd를 사용하여 안정적으로 실행되도록 관리

```bash
#!/bin/bash

BUILD_ID=$1
HOME_DIR=/home/{vm_username}

echo "INFO: Current user: $(whoami)"
echo "INFO: Home directory: $HOME_DIR"

# Secret Manager에서 환경변수 가져오기
echo "INFO: Fetching secrets from Secret Manager..."
JWT_SECRET=$(gcloud secrets versions access latest --secret="jwt-secret")
ES_USERNAME=$(gcloud secrets versions access latest --secret="es-username")
ES_PASSWORD=$(gcloud secrets versions access latest --secret="es-password")
MAIL_USERNAME=$(gcloud secrets versions access latest --secret="mail-username")
MAIL_PASSWORD=$(gcloud secrets versions access latest --secret="mail-password")
GOOGLE_CLIENT_ID=$(gcloud secrets versions access latest --secret="google-client-id")
GOOGLE_CLIENT_SECRET=$(gcloud secrets versions access latest --secret="google-client-secret")
DB_USERNAME=$(gcloud secrets versions access latest --secret="db-username")
DB_PASSWORD=$(gcloud secrets versions access latest --secret="db-password")
CLOUD_SCHEDULER_API_KEY=$(gcloud secrets versions access latest --secret="cloud-scheduler-api-key")
DB_URL=$(gcloud secrets versions access latest --secret="db-url")
DB_URL_DEV=$(gcloud secrets versions access latest --secret="db-url-dev")
ES_URIS=$(gcloud secrets versions access latest --secret="es-uris")
ES_URIS_REPLICA=$(gcloud secrets versions access latest --secret="es-uris-replica")
ES_URIS_DEV=$(gcloud secrets versions access latest --secret="es-uris-dev")
CLOUDRUN_PROJECT_NUMBER=$(gcloud secrets versions access latest --secret="cloudrun-project-number")

# 기존 직접 실행 중인 jar 프로세스 중지
echo "INFO: Checking for existing jar processes..."
OLD_PID=$(ps -ef | grep "java -jar.*mkt-solution-0.0.1-SNAPSHOT.jar" | grep -v grep | awk '{print $2}')
if [ ! -z "$OLD_PID" ]; then
  echo "INFO: Found old process with PID $OLD_PID, terminating..."
  sudo kill -15 $OLD_PID
  sleep 5

  # 프로세스가 여전히 실행 중인지 확인
  if ps -p $OLD_PID > /dev/null; then
    echo "INFO: Process still running, force terminating..."
    sudo kill -9 $OLD_PID
    sleep 2
  fi

  echo "INFO: Old process terminated."
fi

echo "INFO: Downloading new JAR file from GCS"
gsutil cp gs://{gcs_bucket_name}/history/$BUILD_ID-mkt-solution-0.0.1-SNAPSHOT.jar $HOME_DIR/mkt-solution-0.0.1-SNAPSHOT.jar

# systemd 서비스 파일 생성
cat << EOF | sudo tee /etc/systemd/system/{service_name}.service
[Unit]
Description=
After=network.target

[Service]
User={vm_username}
WorkingDirectory=/home/{vm_username}
Environment="JWT_SECRET=${JWT_SECRET}"
Environment="MAIL_USERNAME=${MAIL_USERNAME}"
Environment="MAIL_PASSWORD=${MAIL_PASSWORD}"
Environment="GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}"
Environment="GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}"
Environment="DB_USERNAME=${DB_USERNAME}"
Environment="DB_PASSWORD=${DB_PASSWORD}"
Environment="DB_URL=${DB_URL}"
Environment="DB_URL_DEV=${DB_URL_DEV}"
Environment="ES_URIS=${ES_URIS}"
Environment="ES_URIS_REPLICA=${ES_URIS_REPLICA}"
Environment="ES_URIS_DEV=${ES_URIS_DEV}"
Environment="ES_USERNAME=${ES_USERNAME}"
Environment="ES_PASSWORD=${ES_PASSWORD}"
Environment="CLOUD_SCHEDULER_API_KEY=${CLOUD_SCHEDULER_API_KEY}"
Environment="CLOUDRUN_PROJECT_NUMBER=${CLOUDRUN_PROJECT_NUMBER}"
Environment="GOOGLE_CLOUD_PROJECT=innocean-mkt-datalake-01"

ExecStart=/usr/lib/jvm/java-17-openjdk-amd64/bin/java \
  -Xms4g -Xmx4g \
  -Xlog:gc*,gc+heap=debug:file=/home/{vm_username}/gc.log:time,uptime,level,tags:filecount=5,filesize=50m \
  -XX:+UseG1GC \
  -XX:+UnlockExperimentalVMOptions \
  -XX:G1NewSizePercent=30 \
  -XX:InitiatingHeapOccupancyPercent=30 \
  -XX:G1MaxNewSizePercent=60 \
  -XX:ParallelGCThreads=2 \
  -XX:ConcGCThreads=2 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/home/{vm_username}/heapdump.hprof \
  -Dspring.profiles.active=prod \
  -Duser.timezone=Asia/Seoul \
  -Dlogging.level.com.google.cloud.logging=DEBUG \
  -Dlogging.level.com.google.auth=DEBUG \
  -jar /home/{vm_username}/mkt-solution-0.0.1-SNAPSHOT.jar
SuccessExitStatus=143
StandardOutput=append:/home/{vm_username}/server.log
StandardError=append:/home/{vm_username}/server-error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable {service_name}.service

# 서비스 재시작
sudo systemctl restart {service_name}.service

# 상태 확인
if sudo systemctl is-active --quiet {service_name}.service; then
  echo "INFO: Service started successfully"
  exit 0
else
  echo "ERROR: Failed to start service"
  sudo systemctl status {service_name}.service
  exit 1
fi
```


#### 리전 선택

[본 문서](https://cloud.google.com/build/docs/locations?hl=ko#restricted\_regions\_for\_some\_projects)에 따라 제한이 적은 `asia-east1` 리전을 선택했습니다.

Cloud Build > 트리거에서 수동으로 빌드를 트리거할 수 있고, 대시보드에서 로그 및 상태를 확인할 수 있습니다.
![Cloud Build 개요](/assets/img/cs_cloudbuild/01.png)



#### main 브랜치 protection

Github에서는 main 브랜치에 바로 push하는 것을 막고, develop 브랜치에 먼저 커밋을 모은 뒤 pull request를 통해서만 main에 push할 수 있도록 설정했습니다.&#x20;

Settings > Branches > Add classic branch protection rule 에서 branch rule을 생성할 수 있습니다.

![Main Branch Protection](/assets/img/cs_cloudbuild/02.png)


이렇게 yaml 파일 작성만으로 빌드와 배포를 쉽게 자동화할 수 있습니다. 👍
