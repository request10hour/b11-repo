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

#### 4.1.2 방화벽 설정

##### 4.1.2.1 수행 내역

1. `ubuntu-b11` 환경에서 `ufw`와 `firewall-cmd` 설치 여부를 확인하였다.
2. 두 도구가 모두 설치되어 있지 않아, 과제 확인 방법이 간단한 UFW를 선택하였다.
3. `sudo apt-get install -y ufw`로 UFW를 설치하였다.
4. `sudo ufw default deny incoming`으로 외부에서 들어오는 기본 연결을 차단하였다.
5. `sudo ufw default allow outgoing`으로 서버에서 외부로 나가는 연결은 허용하였다.
6. `sudo ufw allow 20022/tcp`로 SSH 접속용 포트만 허용하였다.
7. `sudo ufw allow 15034/tcp`로 애플리케이션 실행 포트만 허용하였다.
8. `sudo ufw --force enable`로 방화벽을 활성화하고 부팅 시에도 적용되도록 하였다.
9. `sudo ufw status verbose`로 방화벽 상태가 `active`인지 확인하였다.
10. 같은 출력에서 기본 정책이 `deny (incoming)`이고 허용 포트가 `20022/tcp`, `15034/tcp`만 있는지 확인하였다.
11. `sudo ufw status numbered`로 등록된 인바운드 허용 규칙을 번호 목록으로 다시 확인하였다.

##### 4.1.2.2 주요 개념

- UFW란? Uncomplicated Firewall의 약자로, 복잡한 방화벽 규칙을 간단한 명령어로 관리할 수 있게 해주는 Ubuntu의 방화벽 도구이다.
- 인바운드 규칙이란? 외부에서 서버 내부로 들어오는 네트워크 접속을 허용하거나 차단하는 규칙이다.
- 최소 허용 정책이란? 필요한 포트만 열어두고 나머지 접근은 차단하여 공격 가능성을 줄이는 보안 방식이다.

##### 4.1.2.3 확인 결과

- 방화벽 도구 선택: UFW
- 방화벽 상태: `active`
- 기본 인바운드 정책: `deny`
- 허용된 인바운드 포트: `20022/tcp`, `15034/tcp`
- IPv6 규칙도 동일하게 `20022/tcp`, `15034/tcp`만 허용됨

##### 4.1.2.4 증거 자료

UFW 활성화 상태 및 허용 포트 확인:

![UFW 방화벽 상태 확인](screenshots/03_ufw_firewall_status_check.png)

원문 증거 로그:

- `evidence/03_ufw_firewall_status_check.txt`

### 4.2 계정/그룹/권한 체계

#### 4.2.1 생성 계정

##### 4.2.1.1 수행 내역

1. `ubuntu-b11` 환경에서 `getent passwd agent-admin`, `getent passwd agent-dev`, `getent passwd agent-test`로 기존 계정 존재 여부를 확인하였다.
2. 세 계정이 아직 존재하지 않는 것을 확인하였다.
3. `sudo useradd -m -s /bin/bash agent-admin`으로 운영/관리 및 cron 실행 담당 계정을 생성하였다.
4. `sudo useradd -m -s /bin/bash agent-dev`로 개발/운영 및 `monitor.sh` 작성 담당 계정을 생성하였다.
5. `sudo useradd -m -s /bin/bash agent-test`로 QA/테스트 담당 계정을 생성하였다.
6. `id agent-admin`, `id agent-dev`, `id agent-test`로 각 계정의 UID, GID, 기본 그룹을 확인하였다.
7. `getent passwd agent-admin agent-dev agent-test`로 세 계정의 홈 디렉터리와 로그인 shell이 등록되었는지 확인하였다.
8. `ls -ld /home/agent-admin /home/agent-dev /home/agent-test`로 각 계정의 홈 디렉터리가 생성되었는지 확인하였다.

##### 4.2.1.2 주요 개념

- 사용자 계정이란? 리눅스에서 사람 또는 서비스가 시스템 자원에 접근할 때 사용하는 기본 단위이다.
- UID/GID란? UID는 사용자 식별 번호, GID는 그룹 식별 번호로 리눅스가 권한을 판단할 때 사용한다.
- 최소 권한 원칙이란? 계정마다 필요한 역할만 부여하고 불필요한 관리자 권한은 주지 않는 보안 원칙이다.

##### 4.2.1.3 확인 결과

- `agent-admin` 계정 생성 완료: 운영/관리 및 cron 실행자 역할
- `agent-dev` 계정 생성 완료: 개발/운영 및 `monitor.sh` 작성자 역할
- `agent-test` 계정 생성 완료: QA/테스트 역할
- 세 계정 모두 `/home/<계정명>` 홈 디렉터리와 `/bin/bash` shell을 가진 일반 사용자로 생성됨
- 현재 단계에서는 sudo 권한을 추가하지 않아 불필요한 관리자 권한을 부여하지 않음

##### 4.2.1.4 증거 자료

계정 생성 여부, UID/GID, 홈 디렉터리 확인:

![사용자 계정 생성 확인](screenshots/04_user_accounts_check.png)

원문 증거 로그:

- `evidence/04_user_accounts_check.txt`

#### 4.2.2 생성 그룹

##### 4.2.2.1 수행 내역

1. `getent group agent-common`과 `getent group agent-core`로 기존 그룹 존재 여부를 확인하였다.
2. 두 그룹이 아직 존재하지 않는 것을 확인하였다.
3. `sudo groupadd agent-common`으로 공통 협업용 그룹을 생성하였다.
4. `sudo groupadd agent-core`로 핵심 운영 자원 접근용 그룹을 생성하였다.
5. `sudo usermod -aG agent-common agent-admin`으로 `agent-admin`을 `agent-common` 그룹에 추가하였다.
6. `sudo usermod -aG agent-common agent-dev`로 `agent-dev`를 `agent-common` 그룹에 추가하였다.
7. `sudo usermod -aG agent-common agent-test`로 `agent-test`를 `agent-common` 그룹에 추가하였다.
8. `sudo usermod -aG agent-core agent-admin`으로 `agent-admin`을 `agent-core` 그룹에 추가하였다.
9. `sudo usermod -aG agent-core agent-dev`로 `agent-dev`를 `agent-core` 그룹에 추가하였다.
10. `getent group agent-common agent-core`로 두 그룹의 구성원이 요구사항대로 등록되었는지 확인하였다.
11. `id agent-admin`, `id agent-dev`, `id agent-test`로 각 사용자의 실제 보조 그룹 소속을 확인하였다.

##### 4.2.2.2 주요 개념

- 그룹이란? 여러 사용자에게 같은 권한을 한 번에 부여하기 위해 사용하는 리눅스 권한 관리 단위이다.
- 보조 그룹이란? 사용자의 기본 그룹 외에 추가로 소속되는 그룹이며, 공유 디렉터리 접근 권한을 줄 때 활용된다.
- `usermod -aG`란? 기존 그룹 소속을 유지하면서 사용자를 새 보조 그룹에 추가하는 명령이다.

##### 4.2.2.3 확인 결과

- `agent-common` 그룹 생성 완료: `agent-admin`, `agent-dev`, `agent-test` 포함
- `agent-core` 그룹 생성 완료: `agent-admin`, `agent-dev` 포함
- `agent-test`는 `agent-core`에 포함하지 않아 핵심 자원 접근 대상을 제한함
- 역할별 그룹을 분리하여 협업 영역과 핵심 운영 영역을 나눌 준비를 완료함

##### 4.2.2.4 증거 자료

그룹 생성 여부 및 사용자별 그룹 소속 확인:

![사용자 그룹 생성 확인](screenshots/05_user_groups_check.png)

원문 증거 로그:

- `evidence/05_user_groups_check.txt`
