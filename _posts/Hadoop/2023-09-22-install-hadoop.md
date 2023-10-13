---
title: "MAC 하둡 설치"
last_modified_at: 2023-09-22T14:20:00-05:00
layout: post
categories:
    - Hadoop
excerpt: Hadoop 설치
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [Hadoop, 설치]
---

## 1. Homebrew로 하둡 설치

```bash
brew install hadoop

brew info hadoop
# 하둡 설치 위치
## /opt/homebrew/Cellar/hadoop/3.3.6
## Required: openjdk@11
```

### HADOOP 환경변수 설정

```bash
vi ~/.bash_profile

export HADOOP_HOME=/opt/homebrew/Cellar/hadoop/3.3.6/libexec  # 추가
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HADOOP_HOME/lib/native
 
source ~/.bash_profile  # 적용
```

<br>

## 2. JAVA_HOME PATH -> java 1.8.0_371 설정

<!-- ```bash
vi ~/.bash_profile

export JAVA_HOME=/opt/homebrew/Cellar/openjdk@11/11.0.19/libexec/openjdk.jdk/Contents/Home
export PATH=$PATH:$JAVA_HOME/bin

source ~/.bash_profile 
```
```bash
java -version
# openjdk version "11.0.19" 2023-04-18
``` -->


<https://cwiki.apache.org/confluence/display/HADOOP/Hadoop+Java+Versions>

- Java 8 설치 권장

<!-- ```bash
brew install cask

brew tap AdoptOpenJDK/openjdk
brew install --cask adoptopenjdk8

java -version
# java version "1.8.0_371"
``` -->

<br>

### JDK 버전 변경

- 설치된 JDK 버전 확인

```bash
/usr/libexec/java_home -V

# Matching Java Virtual Machines (5):
#     17.0.7 (arm64) "Oracle Corporation" - "Java SE 17.0.7" /Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home
#     1.8.371.11 (x86_64) "Oracle Corporation" - "Java" /Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home
#     1.8.0_371 (x86_64) "Oracle Corporation" - "Java SE 8" /Library/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home
#     1.8.0_292 (x86_64) "AdoptOpenJDK" - "AdoptOpenJDK 8" /Library/Java/JavaVirtualMachines/adoptopenjdk-8.jdk/Contents/Home
# /Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home
```

```bash
export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home

java -version
# openjdk version "1.8.0_371"

echo $JAVA_HOME
# /Library/Java/JavaVirtualMachines/jdk-1.8.jdk/Contents/Home
```

<br>

- `~/.bash_profile` 파일에도 JAVA_HOME 추가

```bash
vi ~/.bash_profile

export JAVA_HOME=/Library/Java/JavaVirtualMachines/adoptopenjdk-8.jdk/Contents/Home  # 추가

source ~/.bash_profile  # 적용
```

<br>

## 3. Hadoop 환경 설정

```bash
cd $HADOOP_HOME/etc/hadoop
```

<br>

### 1) core-site.xml

```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/tmp/hadoop-${user.name}</value>
    </property>
</configuration>
```

<br>

### 2) hdfs-stie.xml

- namenode, datanode 파일 만들어질 `/Users/{user.name}/hadoop` 폴더 만들어놓고 작성

```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/Users/bokyung/hadoop/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/Users/bokyung/hadoop/datanode</value>
    </property>
    <property>
        <name>dfs.namenode.http-address</name>
        <value>localhost:50070</value>
    </property>
    <property>
        <name>dfs.namenode.secondary.http-address</name>
        <value>localhost:50090</value>
    </property>
    <property>
        <name>dfs.datanode.address</name>
        <value>localhost:50010</value>
   </property>
    <property>
        <name>dfs.datanode.http.address</name>
        <value>localhost:50075</value>
    </property>
</configuration>
```

<br>

### 3) mapred-site.xml

```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/:$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/</value>
    </property>
</configuration>
```

<br>

### 4) yarn-site.xml

```xml
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.env-whitelist</name>
        <value>JAVA_HOME,HADOOP_COMMON_HOME,HADOOP_HDFS_HOME,HADOOP_CONF_DIR,CLASSPATH_PREPEND_DISTCACHE,HADOOP_YARN_HOME,HADOOP_HOME,PATH,LANG,TZ,HADOOP_MAPRED_HOME</value>
    </property>
</configuration>
```

<br>

### 5) hadoop-env.sh

- JAVA PATH만 한 번 더 적어주기

```bash
export JAVA_HOME=/opt/homebrew/Cellar/openjdk@11/11.0.19/libexec/openjdk.jdk/Contents/Home
```

<br>

## 4. namenode format

```bash
hdfs namenode -format
```

### 주의할 점!

- 환경 설정을 바꿀 때 hadoop, yarn 종료 후 변경하기
    - `cd $HADOOP_HOME/sbin` -> `stop-yarn.sh` `stop-dfs.sh`
- 변경 후 namenode 포맷 후 재실행
- 포맷 전에 **datanode, namenode 폴더 지우고** 포맷!!!
    - 그렇지 않으면 datanode가 실행되지 않음!
    - `hdfs-site.xml`에서 설정한 폴더
    - 재실행 시 다시 생김

<br>

## 5. Hadoop 실행

```bash
cd $HADOOP_HOME/sbin
start-dfs.sh
start-yarn.sh

jps
# 98658 Jps
# 98034 DataNode
# 98549 NodeManager
# 97924 NameNode
# 98452 ResourceManager
# 98170 SecondaryNameNode
```