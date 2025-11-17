---
title: "[DEV] AWS로 크롤링 자동화하기"
last_modified_at: 2024-07-18T9:00:00-05:00
layout: post
categories:
    - AWS
excerpt: 
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [AWS, crawling]
---

## 배경

- 12개 섹션에 대한 크롤링 + api 수집 작업을 마케터 분이 필요할 때 실행할 수 있도록 자동화 필요
- 12개의 작업은 모두 한 번에 실행되어야 함 (동시성이 중요) - 검색 결과 순위 등을 크롤링하기 때문
- 구글 스프레드 시트에서 키워드 목록을 읽어와 크롤링에 사용하고, 크롤링 결과를 다시 스프레드 시트에 작성해야 함

## ECR 이미지 업로드

1. 각 세션 별로 python 스크립트 작성 -> docker image 생성
2. AWS ECR에 도커 파일 업로드    
    a. `brew install awscli` - awscli 설치    
    b. `aws configure` - aws access key 등록    
    c. ecr 리포지토리 생성 -> 푸시 명령 참고하여 그대로 실행    
    d. `aws ecr get-login-password --region ~` - aws 로그인    
    e. `docker tag {image}:latest {ecr repository}:{new tag}` - 태그 생성    
    &nbsp;&nbsp;&nbsp; - 여러 개의 도커 파일을 생성해야 하기 때문에 같은 리포지토리에 올릴 때 덮어씌워지지 않도록 각각 태그 지정     
    &nbsp;&nbsp;&nbsp; - 태그를 지정하지 않으면 같은 latest 태그를 가진 새로운 이미지가 기존 이미지를 덮어쓰게 됨!    
    f. `docker push {ecr repository}:{new tag}` - 태그 이름으로 ecr 리포지토리에 push


## Batch 작업 생성

- **작업 정의**는 이미지 별로 생성
- chrome을 사용하는 작업은 CPU 8GB, 메모리 16GB로 설정해 둠 + x86_64 아키텍처
- 각 작업에 우선 순위 부여 

## Batch 작업 대기열 생성

- 이 작업 대기열에 12개의 작업을 실행시킬 것!

### fair share scheduling policy 오류

```json
{
  "errorMessage": "An error occurred (ClientException) when calling the SubmitJob operation: Job with shareIdentifier or schedulingPriority can onlybe submitted to job queue with fair share scheduling policy.",
  "errorType": "ClientException",
  "requestId": "c56e0372-bd3b-4e85-9b16-3b563c4cf9af",
  "stackTrace": [
    "  File \"/var/task/lambda_function.py\", line 35, in lambda_handler\n    response = client.submit_job(\n",
    "  File \"/var/lang/lib/python3.12/site-packages/botocore/client.py\", line 553, in _api_call\n    return self._make_api_call(operation_name, kwargs)\n",
    "  File \"/var/lang/lib/python3.12/site-packages/botocore/client.py\", line 1009, in _make_api_call\n    raise error_class(parsed_response, operation_name)\n"
  ]
}
```

- batch 작업 큐가 **공정 공유 스케줄링 정책**을 사용해야 함!
- batch에서 **예약 정책** 생성 -> 작업 대기열에 적용    
    ```bash
    aws batch create-scheduling-policy \
    --name fair-share-policy \
    --fairshare-policy '{"shareDecaySeconds": 3600, "computeReservation": 10, "shareDistribution": [{"shareIdentifier": "Priority1", "weightFactor": 1},{"shareIdentifier": "Priority2", "weightFactor": 2},{"shareIdentifier": "Priority3", "weightFactor": 3},{"shareIdentifier": "Priority4", "weightFactor": 4},{"shareIdentifier": "Priority5", "weightFactor": 5},{"shareIdentifier": "Priority6", "weightFactor": 6},{"shareIdentifier": "Priority7", "weightFactor": 7},{"shareIdentifier": "Priority8", "weightFactor": 8},{"shareIdentifier": "Priority9", "weightFactor": 9},{"shareIdentifier": "Priority10", "weightFactor": 10}]}'
    ```

<br>

- 작업 대기열에 적용시 `Only fairshare queues can have a scheduling policy.` 오류 발생    
    ```bash
    aws batch create-job-queue 
    --job-queue-name crawling-queue \
    --state ENABLED \
    --priority 1 \
    --compute-environment-order computeEnvironment=arn:***:compute-environment/crawling-fargate,order=1 \
    --scheduling-policy-arn arn:***:scheduling-policy/fair-share-policy
    ```

- batch job을 submit하는 lambda 함수에서 `shareIdentifier` 옵션 전달

## Lambda 함수 정의

```python
import boto3

def lambda_handler(event, context):
    client = boto3.client('batch')

    job_queue = "crawling-queue"
    
    job_definitions = [
        "naver-keyword-api",
        "naver-brand-search", 
        "naver-power-link",
        "naver-card-search",
        "naver-snippet",
        "naver-organic",
        "dragon-metrics",
        "google-snippet",
        "google-search",
        "google-search-ads"
    ]
    
    job_names = [
        "naver-keyword-api",
        "naver-brand-search", 
        "naver-power-link",
        "naver-card-search",
        "naver-snippet",
        "naver-organic",
        "dragon-metrics",
        "google-snippet",
        "google-search",
        "google-search-ads"
    ]
    
    priorities = list(range(1, 11)) 
    
    job_list = [
        {"name": name, "shareIdentifier": f"Priority{priority}"}
        for name, priority in zip(job_names, priorities)
    ]

    for job, job_def in zip(job_list, job_definitions):  
        response = client.submit_job(
            jobName=job["name"],
            jobQueue=job_queue,
            jobDefinition=job_def,
            shareIdentifier=job["shareIdentifier"]
        )
        print(f"Submitted {job['name']} with ID: {response['jobId']}")

    return {
        'statusCode': 200,
        'body': 'Batch jobs submitted successfully'
    }
```

- 위 람다 함수를 실행하면 (URL 등) 정의한 batch job들이 작업 대기열에서 실행됨!