---
title: "[pilot] Ch2. 파일럿 프로젝트 아키텍처 설계"
last_modified_at: 2023-09-22T14:45:00-05:00
layout: post
categories:
    - Hadoop
excerpt: 
toc: true
toc_sticky: true
toc_icon: "cog"
author_profile: true
mathjax: true
tag: [study, Hadoop, 파일럿프로젝트]
---

[출처: 실무로 배우는 빅데이터 기술, 김강원 저]

## 1. 설치해야 할 응용프로그램

- JAVA (Java SE 8u-)
- 이클립스
- Oracle Virtual Box
- PuTTY (SSH 접속 프로그램)
- FileZilla (FTP 접속 프로그램)
- Chrome

<br>

## 2. 리눅스 가상머신 환경 구성

### 1) CentOS 설치  

<br>

### 2) 첫번째 리눅스 가상머신 - Server01
![server01](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fb3vETG%2FbtrUHRhRnVm%2FM2sa6PYTnZIBl28ryHX0zk%2Fimg.png)   
- 메모리 2048MB
- 가상 하드 드라이브 동적 할당 30~40GB
- OS: CentOS  

<br>

### 3) 고정 IP, 네트워크 설정

```bash
vi /etc/sysconfig/network-scripts/ifcfg-eth0

# vi: 문서 편집 환경   
# " i " 를 눌러서 입력모드 -> 수정   
# " : "를 눌러서 명령모드   
# 명령모드 진입 후 wq 를 눌러서 저장 후 종료   
```

<br>

- 노란색으로 칠한 두번째 줄은 Server01 가상머신의 MAC 주소로, 가상머신 - [설정] - [네트워크] - [어댑터 2]로 이동해서 나온 MAC 주소 값을 두글자씩 잘라서 `:`로 연결하여 입력하면 됨

![ip](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FobeFR%2FbtrVcnzh1rh%2FWmwznIXVmiVpdkxx22YFsK%2Fimg.png)   

<br>


`/etc/sysconfig/network-scripts`  
  - IP에 대한 설정 스크립트 등 있음    
  - 안에 있는 ifcfg-* 파일 수정하여 IP 변경 (+ GATEWAY, NETMASK, DNS 등 관리)
  - /ifcfg-eth0 : 리눅스 이더넷 카드(네트워크 인터페이스 컨트롤러) 0번 설정 파일


* DEVICE : 네트워크 인터페이스의 종류
* HWADDR : MAC 주소
* ONBOOT : 부팅시 자동 활성 여부
* BOOTPROTO : ip 할당 방식
  - static : 아이피 지정
  - dhcp : 동적 아이피
* IPADDR : IP 주소
* NETMASK : 서브넷 마스크 주소
* GATEWAY : 게이트웨이 주소
* NETWORK : 네트워크 주소


> 리눅스 vi 편집기 명령어 모음 참고   
https://velog.io/@zeesoo/Linux-vi-%ED%8E%B8%EC%A7%91%EA%B8%B0-%EC%82%AC%EC%9A%A9%EB%B2%95-%EB%B0%8F-%EB%AA%85%EB%A0%B9%EC%96%B4

<br>

```bash
vi /etc/udev/rules.d/70-persistent-net.rules
```

- CentOS 리눅스가 기본값으로 설정한 네트워크 룰 삭제하여 향후 발생할 수 있는 네트워크 충돌 방지
- 위의 파일로 들어가서 자동으로 입력되어 있는 값 전부 삭제 또는 주석 처리 (#)
- 이후 앞서 설정한 고정 IP인 '192.168.56.101'을 할당받기 위해 가상머신 재시작

<br>

### 4) 네트워크 서비스에 고정 IP 인식
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdvtOfQ%2FbtrU1Ok2Ey0%2FbzarvbUjDuGp1MAqkok7K1%2Fimg.png)

<br>

```bash
service network restart
```
- restart 명령을 실행한 후, 특별한 오류가 발생하지 않으면 고정 IP 설정이 완료된 것

<br>

### 5) Server01 고정 IP 확인

```bash
ifconfig eth0
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fz36ZO%2FbtrVcmAnHKM%2FqaoIucg6uLHUfkzT279z0K%2Fimg.png)

<br>

### 6) SSH 접속을 위한 패키지 설정

* yum : 패키지 관리 명령어
&nbsp;&nbsp;yum <옵션> <명령어> <패키지명>
* 패키지 설치, 업데이트, 삭제, 패키지 목록 확인 등

<br>

```bash
yum install openssh*        # OpenSSH 설치
service sshd restart
chkconfig sshd on
reboot

# reboot 완료 후
service network restart
```

<br>

## 3. 원격 SSH 접속 프로그램인 PuTTY로 Server01("192.168.56.101") 접속

![putty](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fnpsmw%2FbtrVe3NO0Ni%2FyMA71PVltumw2WTw5k6HY0%2Fimg.png)

<br>

## 4. Server01 호스트 정보 수정

```bash
vi /etc/hosts
```

<br>

__수정 전__

![before](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbdHhdM%2FbtrU541MdRM%2FVOiMPHIqWak5xqqkbWjxSk%2Fimg.png)   

<br>

__수정 후__

![after](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbQK7qe%2FbtrU550G5bc%2FPdHuRoIkvlISxU3C29FzIk%2Fimg.png)  

<br>

- Server01 뿐만 아니라 앞으로 만들 Server02, Server03 IP 및 호스트 정보 설정
- 모두 소문자로 작성

<br>

- __Server01 HOSTNAME 설정__   

```bash
vi /etc/sysconfig/network
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcUpcif%2FbtrU37xJtmb%2F1QLkgnwQpxZA76kepjSlkk%2Fimg.png)  

<br>


* 리눅스 로그인 했을 때 [root@server01 ~]# 
  - root는 사용자 계정
  - server01 이 현재 네트워크의 이름 (호스트명)
  - ~ 는 현재 사용자가 위치한 곳
 

<br>

- __서비스 명령으로 네트워크 설정 재시작__

```bash
service network restart
```

<br>

## 5. Server01 방화벽 및 기타 커널 매개변수 설정

### 1) config 파일에서 SELINUX를 "SELINUX=disabled"로 수정   

* config 파일 : 설정 파일
* SELinux :  관리자가 시스템 액세스 권한을 효과적으로 제어할 수 있게 하는 리눅스 시스템용 보안 아키텍처
  - 시스템 애플리케이션, 프로세스, 파일에 대한 액세스 제어 정의
  - 파일을 여는 프로세스와 같은 엑세스를 명시적으로 허용하는 SELinux 정책 규칙이 없으면 액세스 거부됨

```bash
vi /etc/selinux/config
```

<br>

## 2) iptables 중지 명령   

* iptables : 리눅스에서 방화벽을 설정하는 도구 (패킷필터링 도구)
* 광범위한 프로토콜 상태 추적, 패킷 어플리케이션 계층검사, 속도 제한, 필터링 정책 명시 매커니즘 제공


<br>

```bash
service iptables stop
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fb4QZ0u%2FbtrU9eQpvTB%2Fijj9MjvKtxL4VCjlDykdBK%2Fimg.png)

<br>

> iptables 중지 명령 오류 해결 참고 사이트 (첫번째 답변)  

http://daplus.net/networking-centos-7%EC%97%90%EC%84%9C-iptables%EB%A5%BC-%EC%96%B4%EB%96%BB%EA%B2%8C-%EC%82%AC%EC%9A%A9%ED%95%A0-%EC%88%98-%EC%9E%88%EC%8A%B5%EB%8B%88%EA%B9%8C-%EB%8B%AB%EC%9D%80/
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FYdJ42%2FbtrVeyggpYY%2FaJyxSuedCGWuMlkLYbpD71%2Fimg.png)

<br>


### 3) iptables 자동 시작 중지 명령

```bash
chkconfig iptables off
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcM0NsN%2FbtrU142mW87%2FdeNlXSXRtXPofE5kgKX060%2Fimg.png)   

<br>


### 4) ip6tables 자동 시작 중지 명령    
> ip6tables : IPv6 체계에서 사용   

```bash
chkconfig ip6tables off
```

<br>

### 5) vm swappiness 사용 제어 설정   

* sysctl : (시스템의 /proc/sys 디렉토리 밑에 있는) 커널 변수 값을 제어하여 시스템 최적화
* 일반적으로 커널 매개변수 변경: /proc 디렉토리 밑 항목 vi 편집기 이용하여 변경 / echo 명령 이용
* -w variable=value 옵션: 변수에 값 설정


```bash
sysctl -w vm.swappiness=100
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbwTWxe%2FbtrU56ZEvJW%2FyPZbgvHJ5qNwMWr3xIRzd1%2Fimg.png)   
<br>

### 6) sysctl.conf 파일에서 "vm.swappiness=100" 설정 추가  

* vm.swappiness : 리눅스 커널 속성 중 하나로 스왑메모리 활용 수준 조절
* Swap 메모리 : 실제 메모리 램이 가득 찼지만 더 많은 메모리가 필요할 때, 디스크 공간을 이용하여 부족한 메모리를 대체할 수 있는 공간 (실제 디스크 공간을 메모리처럼 사용하는 개념 -> 가상 메모리라고 할 수 있음)
* 리눅스에서 Swap : 실제 메모리에 올라와 있는 메모리 블록들 중 당장 쓰이지 않는 것을 디스크에 저장하고, 이를 통해 가용 메모리 영역 늘림


![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdIOLPb%2FbtrU293wLVU%2FOKfqyqozSCs50ZxptyZ7vK%2Fimg.png)      
<br>

```bash
vi /etc/sysctl.conf
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FZuePq%2FbtrVfjiHi0N%2FDbg81AkD7AbR11QEr7eb3K%2Fimg.png)   
<br>

### 7) rc.local 파일에서 아래 명령어 추가   

> rc.local 파일 : 부팅시 자동실행 명령어 스크립트를 수행하며, 일반적으로 서버 부팅시마다 매번 자동 실행되기를 원하는 명령어를 넣음   

> transparent_hugepage 설명   
https://hoing.io/archives/809

<br>

```bash
vi /etc/rc.local

# 서비스 생성 및 등록 -> transparnet huge page 비활성화
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FOr6CK%2FbtrU6XuGLGO%2FeYHyAtagrxHD1wxrXKZ2Ok%2Fimg.png)

<br>

### 8) limits.conf 파일에서 아래의 파일 디스크립터 설정 추가   

* limits.conf 파일 : 서버 리소스 관리 - 서버 다운 예방
  <domain> <type> <item> <value> 로 추가 입력

* <domain> : 제한할 대상 작성 (*, user명, 그룹명(@)) 

* <type>
  - soft : 새로운 프로그램을 생성하면 기본으로 적용되는 한도 (이 용량 넘으면 경고 메시지)
  - hard : 최대로 늘릴 수 있는 한도 (어떠한 일이 있어도 이 용량을 넘을 수 없음)
  - 통상적으로 soft와 hard 1:1로 맞추어 설정

* <item>
  - nproc (number of processes) : 최대 프로세스 개수 (KB)
  - nofile (number of open files) : 한 번에 열 수 있는 최대 파일 수 
  - 리눅스에서는 모든 개체를 파일로 보기에 nproc을 높이면 nofile도 같이 올려줄 것

* <value> : 제한하고자 하는 설정값


```bash
vi /etc/security/limits.conf

root soft nofile 65536
root hard nofile 65536
*    soft nofile 65536
*    hard nofile 65536
root soft nproc 32768
root hard nproc 32768
*    soft nproc 32768
*    hard nproc 32768

# 서버 리부팅
reboot
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbFn3iU%2FbtrU2LBQRNK%2FUUf6jOSwxkxZpkQJAK9aN1%2Fimg.png)   

<br>

- __5번 과정 명령어 모음__

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fz8RFD%2FbtrVex9BAqd%2F5Tdm9sADe6MJJcwtFM5Ik0%2Fimg.png)   

<br>

## 6. 가상머신 복제

### 1) 복제 대상인 Server01 전원 끄고, 복제 작업이 완료될 때까지 시작하지 않음

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FOcwAr%2FbtrVe3OeRL1%2FkpcdQfKPapAZWMz7ux5kn0%2Fimg.png)

### 2) Server01 우클릭하여 "복제" 클릭

### 3) 이름은 "Server02"로, "모든 네트워크 카드의 MAC 주소 초기화" 체크

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FrpauD%2FbtrVgiqCAun%2F9ZCnvjBysq5MWNIU8KN1aK%2Fimg.png)   

<br>

## 7. Server02 설정 수정

### 1) MAC 주소, 고정 IP 수정

```bash
vi /etc/sysconfig/network-scripts/ifcfg-eth0
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FEEt6R%2FbtrVeWuRhCR%2FJp5iS6DGGG2ndIJg9u781K%2Fimg.png)   

- 노란색으로 칠해져 있는 부분 (MAC 주소, IP 주소) 수정


### 2) 리눅스가 자동으로 설정한 Server01 네트워크 룰 삭제

```bash
vi /etc/udev/rules.d/70-persistent-net.rules
```

- 쓰여있는 내용 전부 주석 처리 / 삭제

### 3) Server02 종료 후 다시 시작 -> 새로운 네트워크 정보 할당

### 4) Server02 호스트 정보 수정

```bash
vi /etc/hosts
```

![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FcdEDrc%2FbtrVgj39Jwe%2FQUklUOy5KLplvB0skZle1K%2Fimg.png)   

### 5) Server02 호스트명 수정

```bash
vi /etc/sysconfig/network
```
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FlfBqW%2FbtrU44urqBk%2FLHqBZKDCIWKHQSvfEDi4S1%2Fimg.png)   

### 6) 네트워크 설정 정보 재시작 및 운영체제 리부트
```bash
service network restart
reboot
```

### 7) 네트워크 설정 반영 확인
```bash
ifconfig eth0
hostname
```
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fcz7v2x%2FbtrU44H3u6b%2FfkrvGM7ZZEzVzU9CyLyi80%2Fimg.png)   

<br>

# 8. Server03 복제 (고사양 파일럿 아키텍처)

- Server02 복제와 같은 순서로 진행
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fc80ePQ%2FbtrVcnzJ2kG%2FPUQVFZdbVdk8SIQoEyCzY0%2Fimg.png) 

<br>

## 9. 가상머신 CPU와 메모리 리소스 설정 최적화

- 고사양 파일럿 아키텍처 (CPU: i5 이상, 메모리: 16GB)
- Server01, Server02: 5120MB, Server03: 3072MB

<br>

## 10. 고정 IP 주소로 PuTTY 접속환경 구성
![](https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdZBgvU%2FbtrVfs1k6eZ%2F49303KXuRdsp93P37fqX41%2Fimg.png)

- Host name과 Saved Sessions을 적고 Save로 저장해둠