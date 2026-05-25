# B1-1. 시스템 관제 자동화 스크립트 개발 수행내역서

## 1. 미션 소개

서버 운영 환경에서 장애 원인을 확인하려면 보안 설정, 네트워크 상태, 로그 기록이 중요하다고 판단하였다. 이번 수행에서는 우선 SSH 접속 포트를 변경하고 Root 원격 접속을 차단하여 기본 보안 설정을 적용하였다.

## 2. 최종 결과물

- 수행내역서: `README.md`
- 증거 이미지 폴더: `screenshots/`
- 원문 증거 로그 폴더: `evidence/`
- SSH 설정 파일 백업용 제출 자료: `config/99-b11-hardening.conf`

## 3. 과제 목표

SSH 기본 포트인 22번을 그대로 사용하면 자동 스캔 및 무작위 로그인 시도 대상이 되기 쉽다. 그래서 포트를 `20022`로 변경하고, 관리자 계정인 root의 원격 로그인을 막아 일반 계정 기반으로 접근하도록 구성하였다.

## 4. 기능 요구 사항

### 4.1 기본 보안 및 네트워크 설정

#### 4.1.1 SSH 설정

##### 4.1.1.1 수행 내역

1. `ubuntu-b11` 환경에서 `sshd` 설치 여부를 확인하였다.
2. `sshd`가 설치되어 있지 않아 `sudo apt-get update`를 실행하였다.
3. `sudo apt-get install -y openssh-server`로 OpenSSH 서버를 설치하였다.
4. 제출 저장소에 `config/99-b11-hardening.conf` 파일을 만들었다.
5. 해당 설정 파일에 `Port 20022`를 작성하여 SSH 접속 포트를 20022번으로 지정하였다.
6. 같은 설정 파일에 `PermitRootLogin no`를 작성하여 Root 원격 로그인을 차단하였다.
7. `/etc/ssh/sshd_config.d/` 디렉터리를 생성하고 설정 파일을 배포하였다.
8. `sudo sshd -t`로 SSH 설정 문법 오류가 없는지 확인하였다.
9. Ubuntu 24.04 환경에서 기본 `ssh.socket`이 22번 포트를 잡고 있어 `sudo systemctl disable --now ssh.socket`으로 비활성화하였다.
10. `sudo systemctl enable ssh.service`로 SSH 서비스를 부팅 시 자동 실행되도록 등록하였다.
11. `sudo systemctl restart ssh.service`로 변경된 설정을 적용하였다.
12. `sshd_config.d` 설정 파일에서 `Port 20022`, `PermitRootLogin no`가 들어간 것을 확인하였다.
13. `sudo sshd -T`로 실제 적용된 설정도 `port 20022`, `permitrootlogin no`임을 확인하였다.
14. `sudo ss -tulnp`로 `sshd`가 `0.0.0.0:20022`와 `[::]:20022`에서 LISTEN 상태임을 확인하였다.

##### 4.1.1.2 주요 개념

- SSH란? 원격 서버에 암호화된 방식으로 접속하기 위한 프로토콜이며, 서버 관리에 자주 사용된다.
- `PermitRootLogin`이란? root 계정의 SSH 직접 접속 허용 여부를 정하는 설정이다. `no`로 설정하면 root 직접 접속을 막아 보안을 높일 수 있다.
- `ss`란? 소켓 통계(Socket Statistics)를 확인하는 도구로, 네트워크 연결 상태를 보여주는 `netstat`의 대체 도구로 널리 사용된다.

##### 4.1.1.3 확인 결과

- SSH 포트 변경: `20022` 적용 완료
- Root 원격 접속 차단: `PermitRootLogin no` 적용 완료
- SSH 서비스 상태: `active`, `enabled`
- 포트 리슨 상태: `sshd`가 `20022/tcp`에서 LISTEN 중

##### 4.1.1.4 증거 자료

SSH 설정 파일 및 실제 적용 설정 확인:

![SSH 설정 파일 확인](screenshots/01_ssh_config_check.png)

SSH 서비스 상태 및 포트 리슨 확인:

![SSH 포트 리슨 확인](screenshots/02_ssh_port_listen_check.png)

원문 증거 로그:

- `evidence/01_ssh_config_check.txt`
- `evidence/02_ssh_port_listen_check.txt`

