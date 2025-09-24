


## Docker - Microsoft 실습

<https://learn.microsoft.com/ko-kr/visualstudio/docker/tutorials/docker-tutorial> 실습입니다.

### 이미지 pull & 컨테이너 실행

```bash
docker run -d -p 8080:80 docker/getting-started
```

- `-d` : 백그라운드에서 분리 모드로 컨테이너 실행
- `-p 8080:80` : 호스트 포트 8080을 컨테이너 포트 80에 매핑
- `docker/getting-started` : 사용할 이미지

<br>

<img width="690" alt="스크린샷 2023-12-10 오전 10 55 27" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/4db6a0e8-c5ae-46b2-89bf-9552b80a601f">

<img width="1269" alt="스크린샷 2023-12-10 오전 10 55 36" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/463e3b2e-eba1-456f-b9cb-2645fb84950a">

### 브라우저에서 확인

<http://localhost:8080/tutorial>

<img width="950" alt="스크린샷 2023-12-10 오전 10 58 57" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/074d9b81-e0a4-4a80-823c-1b62e3ae0b17">

### 컨테이너 삭제

```bash
# 컨테이너 확인
docker ps

# 중지 및 제거
docker stop <container-id>
docker rm <container-id>
```

### Todo 앱 이미지 빌드

<https://github.com/docker/getting-started/tree/master> 이 레포지토리의 **app** 파일을 로컬 파일에 복사

<br>

- pakage.json

```json
{
  "name": "101-app",
  "version": "1.0.0",
  "main": "index.js",
  "license": "MIT",
  "scripts": {
    "prettify": "prettier -l --write \"**/*.js\"",
    "test": "jest",
    "dev": "nodemon src/index.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "mysql2": "^2.3.3",
    "sqlite3": "^5.1.2",
    "uuid": "^9.0.0",
    "wait-port": "^1.0.4"
  },
  "resolutions": {
    "ansi-regex": "5.0.1"
  },
  "prettier": {
    "trailingComma": "all",
    "tabWidth": 4,
    "useTabs": false,
    "semi": true,
    "singleQuote": true
  },
  "devDependencies": {
    "jest": "^29.3.1",
    "nodemon": "^2.0.20",
    "prettier": "^2.7.1"
  }
}
```

<br>

- Dockerfile

```dockerfile
FROM node:20-alpine
RUN apk add --no-cache python3 g++ make
WORKDIR /app
COPY . .
RUN yarn install --production
CMD ["node", "/app/src/index.js"]
```

- 베이스 이미지: node:20-alpine
- 이미지 생성 시 `apk add --no-cache python3 g++ make` 명령 실행
    - python3, g++ (GNU C++ 컴파일러), make 도구를 이미지에 설치
    - `--no-cache` 옵션: 패키지 설치 후 캐시 삭제 -> 이미지 크기 줄임
- 도커 이미지 내에서 /app 디렉토리가 작업 디렉토리로 설정됨
- 현재 도커 파일이 위치한 디렉토리의 모든 파일과 디렉토리를 작업 디렉토리(/app)에 복사
- `RUN yarn install --production`: 애플리케이션의 종속성 설치 
    - `--production`: 개발용 종속성을 제외하고 프로덕션용 종속성만 설치
- `CMD ["node", "/app/src/index.js"]`: 컨테이너 실행 시 기본으로 실행되는 명령
    - 애플리케이션의 엔트리 포인트인 /app/src/index.js을 Node.js로 실행

<br>

- 이미지 빌드
    - `-t` : 태그
    - `.` : 현재 위치에서 **Dockerfile**을 찾도록

```bash
docker build -t getting-started .
```

<img width="898" alt="스크린샷 2023-12-10 오후 12 00 37" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/15987c67-1eda-4278-98e8-7011ea1e2291">

<img width="903" alt="스크린샷 2023-12-10 오전 11 59 47" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/e9b839af-80ed-407b-9c4d-6b31cefafbff">



### 컨테이너 시작

```bash
docker run -dp 3000:3000 getting-started
```

<img width="717" alt="스크린샷 2023-12-10 오후 12 01 20" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/dbccca52-419b-43d9-ae50-34e841cc9a58">

<br>

<http://localhost:3000>

<img width="949" alt="스크린샷 2023-12-10 오후 12 01 51" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/2a1a6fbb-fec8-41d1-9f3d-23e866eb112a">


### 코드 업데이트

- src/static/js/app.js 파일에서 코드 변경
- 컨테이너 중지 후 제거
- 이미지 빌드 후 컨테이너 시작

### 이미지 Push

- Docker Hub에서 리포지토리 생성

<img width="1377" alt="스크린샷 2023-12-10 오후 1 40 38" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/cd3bc90e-3cdd-4717-b73f-56839ab15ba2">

<br>

- 터미널에서 도커 허브 로그인

```bash
docker login -u <user name>
```

- 이미지 업로드

```bash
docker tag getting-started bokyung2/getting-started

docker push bokyung2/getting-started
```

<img width="646" alt="스크린샷 2023-12-10 오후 2 02 14" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/f0dac9be-5496-4005-9d1f-db395d2a21f7">

<img width="1261" alt="스크린샷 2023-12-10 오후 2 05 44" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/7971997d-8561-4683-a2a9-f3de31e4c7ed">

### 볼륨 사용

- 한 컨테이너에서 만들어진 파일은 다른 컨테이너에서 사용할 수 없음!
- **볼륨**을 만들어 데이터를 저장하는 폴더에 연결하면 해당 데이터는 볼륨의 호스트에 유지됨

<br>

- 볼륨 생성

```bash
docker volume create todo-db
```

<br>

- 컨테이너 중지 후 볼륨을 연결하여 다시 시작
    - `-v` : 탑재할 볼륨과 위치 지정

```bash
docker run -dp 3000:3000 -v todo-db:/etc/todos getting-started
```

<br>

-  브라우저 새로고침 후 항목 추가


<img width="887" alt="스크린샷 2023-12-10 오후 2 21 55" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/cac20a7c-a046-4fb2-8135-87432a6e08a0">

<br>

- getting-started 컨테이너 제거 후 다시 새로운 컨테이너 시작
    - 데이터가 남아있음!

```bash
docker run -dp 3000:3000 -v todo-db:/etc/todos getting-started
```

<img width="891" alt="스크린샷 2023-12-10 오후 2 23 33" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/62529fdd-10a9-44b6-96f0-ca180d9c0f44">

### 데이터가 저장되는 위치 확인

```bash
docker volume inspect todo-db
```

- 결과
    - `Mountpoint`가 데이터가 저장되는 실제 위치

```json
[
    {
        "CreatedAt": "2023-12-10T05:18:27Z",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/todo-db/_data",
        "Name": "todo-db",
        "Options": null,
        "Scope": "local"
    }
]
```

### 이미지 계층 보기

```bash
docker image history --no-trunc getting-started
```

<img width="818" alt="스크린샷 2023-12-10 오후 5 24 29" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/69847c4f-30c6-4669-a142-baf3dac1f74f">

## docker compose



### 다른 컨테이너와 통신할 수 있도록 **네트워크** 배치

```bash
# 네트워크 생성
docker network create todo-app

# MySQL 컨테이너 시작
docker run -d
    --network todo-app --network-alias mysql
    -v todo-mysql-data:/var/lib/mysql
    -e MYSQL_ROOT_PASSWORD=<pwd>
    -e MYSQL_DATABASE=todos
    mysql:5.7
```

<img width="657" alt="스크린샷 2023-12-10 오후 5 31 26" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/51238ed1-6536-495f-8b2e-24eb13a4a0a2">

<img width="1072" alt="스크린샷 2023-12-10 오후 5 31 38" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/c9029d72-bcca-4336-9416-95459003cfe6">


### mysql 연결 확인

```bash
docker exec -it <mysql container id> mysql -p
```

<img width="724" alt="스크린샷 2023-12-10 오후 5 32 44" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/68f3068a-7ecf-4931-acfb-436ed60735d5">

### `todo` 데이터베이스 확인

<img width="269" alt="스크린샷 2023-12-10 오후 5 33 31" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/3fe994fa-36a9-48bf-8989-1d9468129ab3">

### docker compose 파일 생성

- `docker-compose.yml`

```yaml
version: "3.7"

services:
    app:
        image: node:20-alpine
        command: sh -c "yarn install && yarn run dev"
        ports:
            - 3000:3000
        working_dir: /app
        volumes:
            - ./:/app
        environment:
            MYSQL_HOST: mysql
            MYSQL_USER: root
            MYSQL_PASSWORD: <pwd>
            MYSQL_DB: todos
    mysql:
        image: mysql:8.2.0
        volumes:
            - todo-mysql-data: /var/lib/mysql
        environments:
            MYSQL_ROOT_PASSWORD: <pwd>
            MYSQL_DATABASE: todos

# 볼륨 매핑 정의
volumes:
    todo-mysql-data:
```

### docker compose 실행 및 제거

```bash
docker-compose up -d
```

<img width="589" alt="스크린샷 2023-12-11 오후 2 09 27" src="https://github.com/bokyung124/AWS_Exercise/assets/53086873/52e49133-d8cb-41c6-ac11-b982d7251931">

<br>

```bash
docker-compose down
```