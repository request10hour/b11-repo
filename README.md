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

#### 4.2.3 디렉토리 구조

##### 4.2.3.1 수행 내역

1. 과제 예시를 참고하여 `AGENT_HOME` 기준 경로를 `/home/agent-admin/agent-app`으로 정하였다.
2. `test -d /home/agent-admin/agent-app`로 앱 홈 디렉터리 존재 여부를 확인하였다.
3. `test -d /home/agent-admin/agent-app/upload_files`로 업로드 디렉터리 존재 여부를 확인하였다.
4. `test -d /home/agent-admin/agent-app/api_keys`로 키 파일 보관 디렉터리 존재 여부를 확인하였다.
5. `test -d /var/log/agent-app`로 앱 로그 디렉터리 존재 여부를 확인하였다.
6. 네 디렉터리가 아직 없는 것을 확인하였다.
7. `sudo install -d -o agent-admin -g agent-admin -m 750 /home/agent-admin/agent-app`으로 `AGENT_HOME` 디렉터리를 생성하였다.
8. `sudo install -d -o agent-admin -g agent-admin -m 750 /home/agent-admin/agent-app/upload_files`로 업로드 파일 디렉터리를 생성하였다.
9. `sudo install -d -o agent-admin -g agent-admin -m 750 /home/agent-admin/agent-app/api_keys`로 API 키 디렉터리를 생성하였다.
10. `sudo install -d -o root -g root -m 755 /var/log/agent-app`로 애플리케이션 로그 디렉터리를 생성하였다.
11. `ls -ld`로 `AGENT_HOME`, `upload_files`, `api_keys`, `/var/log/agent-app`가 모두 생성되었는지 확인하였다.
12. `find` 명령으로 앱 홈 하위 디렉터리 구조와 `/var/log/agent-app` 경로를 다시 확인하였다.

##### 4.2.3.2 주요 개념

- `AGENT_HOME`이란? 애플리케이션 실행에 필요한 파일과 하위 디렉터리를 모아두는 기준 경로이다.
- `install -d`란? 디렉터리를 만들면서 소유자, 그룹, 권한을 함께 지정할 수 있는 명령이다.
- 로그 디렉터리란? 애플리케이션 실행 기록이나 관제 결과를 저장하는 전용 위치이다.

##### 4.2.3.3 확인 결과

- `AGENT_HOME` 생성 완료: `/home/agent-admin/agent-app`
- 업로드 디렉터리 생성 완료: `/home/agent-admin/agent-app/upload_files`
- API 키 디렉터리 생성 완료: `/home/agent-admin/agent-app/api_keys`
- 로그 디렉터리 생성 완료: `/var/log/agent-app`
- 이번 단계에서는 디렉터리 구조 생성을 완료하였고, 그룹별 접근 권한은 다음 권한 설정 단계에서 세부 조정할 예정이다.

##### 4.2.3.4 증거 자료

`AGENT_HOME` 기준 디렉터리 구조 및 로그 디렉터리 확인:

![디렉토리 구조 확인](screenshots/06_directory_structure_check.png)

원문 증거 로그:

- `evidence/06_directory_structure_check.txt`

#### 4.2.4 접근 권한

##### 4.2.4.1 수행 내역

1. `command -v getfacl`과 `command -v setfacl`로 ACL 확인 도구 설치 여부를 확인하였다.
2. ACL 도구가 설치되어 있지 않아 `sudo apt-get install -y acl`로 `acl` 패키지를 설치하였다.
3. `id agent-admin`, `id agent-dev`, `id agent-test`로 각 계정의 그룹 소속을 다시 확인하였다.
4. `/home/agent-admin`은 다른 사용자에게 기본 접근이 막혀 있으므로 `sudo setfacl -m g:agent-common:x /home/agent-admin`으로 필요한 경로 탐색 권한만 부여하였다.
5. `sudo chown agent-admin:agent-common /home/agent-admin/agent-app`으로 `AGENT_HOME`의 그룹을 공통 그룹 기준으로 맞추었다.
6. `sudo chmod 2750 /home/agent-admin/agent-app`으로 그룹이 읽고 들어갈 수 있게 하고, setgid 비트를 적용하였다.
7. `sudo chown agent-admin:agent-common /home/agent-admin/agent-app/upload_files`로 `upload_files`의 그룹을 `agent-common`으로 지정하였다.
8. `sudo chmod 2770 /home/agent-admin/agent-app/upload_files`로 `agent-common` 그룹 구성원이 읽고 쓸 수 있게 설정하였다.
9. `sudo chown agent-admin:agent-core /home/agent-admin/agent-app/api_keys`로 `api_keys`의 그룹을 `agent-core`로 지정하였다.
10. `sudo chmod 2770 /home/agent-admin/agent-app/api_keys`로 `agent-core` 그룹만 읽고 쓸 수 있게 설정하였다.
11. `sudo chown root:agent-core /var/log/agent-app`로 로그 디렉터리 그룹을 `agent-core`로 지정하였다.
12. `sudo chmod 2770 /var/log/agent-app`로 `agent-core` 그룹만 로그 디렉터리에 읽기/쓰기 가능하도록 설정하였다.
13. `setfacl -d`로 `upload_files`, `api_keys`, `/var/log/agent-app`에 기본 ACL을 설정하여 새 파일도 그룹 권한을 유지하도록 하였다.
14. `ls -ld`로 각 디렉터리의 소유자, 그룹, 권한을 확인하였다.
15. `getfacl`로 ACL 및 기본 ACL 적용 상태를 확인하였다.
16. `agent-admin`, `agent-dev`, `agent-test` 계정으로 `upload_files` 쓰기 테스트를 하여 세 계정 모두 쓰기 가능함을 확인하였다.
17. `agent-admin`, `agent-dev` 계정으로 `api_keys` 쓰기 테스트를 하여 `agent-core` 구성원만 쓰기 가능함을 확인하였다.
18. `agent-test` 계정으로 `api_keys` 쓰기 테스트를 하여 접근이 거부되는 것을 확인하였다.
19. `agent-admin`, `agent-dev` 계정으로 `/var/log/agent-app` 쓰기 테스트를 하여 `agent-core` 구성원만 쓰기 가능함을 확인하였다.
20. `agent-test` 계정으로 `/var/log/agent-app` 쓰기 테스트를 하여 접근이 거부되는 것을 확인하였다.

##### 4.2.4.2 주요 개념

- R/W 권한이란? 읽기(Read)와 쓰기(Write) 권한을 의미하며, 디렉터리에서는 파일 목록 확인과 파일 생성/수정에 영향을 준다.
- ACL이란? 기본 소유자/그룹/기타 권한보다 세밀하게 접근 권한을 지정할 수 있는 리눅스 권한 기능이다.
- setgid 디렉터리란? 디렉터리 안에 새 파일을 만들 때 부모 디렉터리의 그룹을 이어받게 하는 설정이다.

##### 4.2.4.3 확인 결과

- `upload_files`: 그룹 `agent-common`, 권한 `rwx`로 설정되어 `agent-admin`, `agent-dev`, `agent-test` 모두 R/W 가능
- `api_keys`: 그룹 `agent-core`, 권한 `rwx`로 설정되어 `agent-admin`, `agent-dev`만 R/W 가능
- `/var/log/agent-app`: 그룹 `agent-core`, 권한 `rwx`로 설정되어 `agent-admin`, `agent-dev`만 R/W 가능
- `agent-test`는 `agent-core`에 속하지 않기 때문에 `api_keys`와 `/var/log/agent-app` 쓰기가 거부됨
- `other` 권한은 `---`로 두어 그룹 외 사용자의 접근을 차단함

##### 4.2.4.4 증거 자료

계정 그룹 소속, 디렉터리 소유/권한, ACL 확인:

![접근 권한 메타데이터 확인](screenshots/07_access_permission_metadata_check.png)

사용자별 쓰기 가능 여부 확인:

![접근 권한 쓰기 테스트](screenshots/08_access_permission_write_tests.png)

원문 증거 로그:

- `evidence/07_access_permission_metadata_check.txt`
- `evidence/08_access_permission_write_tests.txt`

### 4.3 애플리케이션 실행 환경 구성

#### 4.3.1 환경 변수

##### 4.3.1.1 수행 내역

1. `uname -m`으로 `ubuntu-b11`의 CPU 아키텍처가 `x86_64`인지 확인하였다.
2. `/Users/10hour0574/Downloads/pjt7ec757e6-0e57-48e9-9805-e1587f441508_agent-app.zip`에 제공 애플리케이션 zip 파일이 있는지 확인하였다.
3. `python3 -m zipfile -l`로 zip 내부에 `agent-app`과 `agent-app-linux-arm64`가 들어 있는 것을 확인하였다.
4. 현재 환경은 `x86_64`이므로 임의 앱을 만들지 않고 제공 파일 중 `agent-app`을 사용하기로 하였다.
5. `python3 -m zipfile -e`로 제공 zip을 `/tmp/b11-agent-app-extract`에 압축 해제하였다.
6. `sudo install -o agent-admin -g agent-core -m 750 /tmp/b11-agent-app-extract/agent-app /home/agent-admin/agent-app/agent-app`으로 제공 앱을 `AGENT_HOME` 아래에 배치하였다.
7. 제출 저장소에 `config/agent-app-env.sh` 파일을 작성하였다.
8. 환경 변수 파일에 `AGENT_HOME=/home/agent-admin/agent-app`을 등록하였다.
9. 환경 변수 파일에 `AGENT_PORT=15034`를 등록하였다.
10. 환경 변수 파일에 `AGENT_UPLOAD_DIR=$AGENT_HOME/upload_files`를 등록하였다.
11. 환경 변수 파일에 `AGENT_KEY_PATH=$AGENT_HOME/api_keys/t_secret.key`를 등록하였다.
12. 환경 변수 파일에 `AGENT_LOG_DIR=/var/log/agent-app`를 등록하였다.
13. `sudo install -o root -g root -m 644 config/agent-app-env.sh /etc/profile.d/agent-app.sh`로 시스템 로그인 셸에서 환경 변수가 자동 등록되도록 배포하였다.
14. `sudo cat /etc/profile.d/agent-app.sh`로 시스템에 등록된 환경 변수 파일 내용을 확인하였다.
15. `sudo -u agent-admin bash -lc ...`로 `agent-admin` 로그인 셸에서 환경 변수들이 실제 값으로 로드되는 것을 확인하였다.
16. `ls -l`로 제공 앱 파일, 업로드 디렉터리, 키 디렉터리, 로그 디렉터리가 환경 변수 경로와 맞는지 확인하였다.
17. `test -x "$AGENT_HOME/agent-app"`로 제공 앱 파일이 실행 가능 상태인지 확인하였다.

##### 4.3.1.2 주요 개념

- 환경 변수란? 프로그램 실행 시 필요한 경로, 포트, 설정값을 코드 밖에서 전달하기 위한 값이다.
- `/etc/profile.d`란? 로그인 셸이 시작될 때 공통 환경 설정 스크립트를 읽는 디렉터리이다.
- `AGENT_HOME`이란? 앱 실행 파일과 관련 디렉터리를 찾기 위한 기준 경로이다.

##### 4.3.1.3 확인 결과

- 제공 앱 zip 사용 확인: `pjt7ec757e6-0e57-48e9-9805-e1587f441508_agent-app.zip`
- 선택한 앱 파일: `agent-app` (`x86_64` 환경 기준)
- 앱 배치 경로: `/home/agent-admin/agent-app/agent-app`
- 환경 변수 등록 파일: `/etc/profile.d/agent-app.sh`
- `AGENT_HOME`: `/home/agent-admin/agent-app`
- `AGENT_PORT`: `15034`
- `AGENT_UPLOAD_DIR`: `/home/agent-admin/agent-app/upload_files`
- `AGENT_KEY_PATH`: `/home/agent-admin/agent-app/api_keys/t_secret.key`
- `AGENT_LOG_DIR`: `/var/log/agent-app`
- `agent-admin` 로그인 셸에서 환경 변수가 정상적으로 로드됨
- 키 파일 자체는 다음 단계에서 생성할 예정이며, 이번 단계에서는 키 파일 경로 환경 변수를 먼저 고정함

##### 4.3.1.4 증거 자료

제공 앱 zip 확인, 환경 변수 등록 파일, `agent-admin` 계정의 환경 변수 로드 확인:

![애플리케이션 환경 변수 확인](screenshots/09_agent_environment_variables_check.png)

원문 증거 로그:

- `evidence/09_agent_environment_variables_check.txt`

#### 4.3.2 키 파일 생성

##### 4.3.2.1 수행 내역

1. `sudo -u agent-admin bash -lc 'printf "%s\n" "$AGENT_KEY_PATH"'`로 환경 변수에 등록된 키 파일 경로를 확인하였다.
2. `test -f /home/agent-admin/agent-app/api_keys/t_secret.key`로 기존 키 파일 존재 여부를 확인하였다.
3. 키 파일이 아직 존재하지 않는 것을 확인하였다.
4. `sudo -u agent-admin bash -lc 'printf "agent_api_key_test\n" > "$AGENT_KEY_PATH"'`로 키 파일을 생성하였다.
5. `sudo chown agent-admin:agent-core /home/agent-admin/agent-app/api_keys/t_secret.key`로 키 파일 소유자와 그룹을 지정하였다.
6. `sudo chmod 660 /home/agent-admin/agent-app/api_keys/t_secret.key`로 소유자와 `agent-core` 그룹만 읽고 쓸 수 있게 설정하였다.
7. `ls -l`로 키 파일의 소유자, 그룹, 권한을 확인하였다.
8. `wc -l`로 키 파일 내용이 1줄인지 확인하였다.
9. `cat`으로 키 파일 내용이 `agent_api_key_test`인지 확인하였다.
10. `agent-admin` 계정에서 `test "$(cat "$AGENT_KEY_PATH")" = "agent_api_key_test"`로 앱 실행 계정 기준에서도 내용 검증이 되는지 확인하였다.

##### 4.3.2.2 주요 개념

- 키 파일이란? 앱이 실행될 때 인증 값이나 비밀 값을 파일로 읽을 수 있도록 저장한 파일이다.
- `chmod 660`이란? 소유자와 그룹에는 읽기/쓰기 권한을 주고, 기타 사용자에게는 권한을 주지 않는 설정이다.
- `wc -l`이란? 파일의 줄 수를 확인하는 명령으로, 이번에는 키 값이 한 줄로 저장되었는지 확인하는 데 사용하였다.

##### 4.3.2.3 확인 결과

- 키 파일 경로: `/home/agent-admin/agent-app/api_keys/t_secret.key`
- 키 파일 내용: `agent_api_key_test`
- 줄 수: `1`
- 소유자/그룹: `agent-admin:agent-core`
- 권한: `-rw-rw----`
- `agent-admin` 계정 기준으로 환경 변수 경로와 실제 키 파일 내용이 일치함

##### 4.3.2.4 증거 자료

키 파일 경로, 권한, 줄 수, 내용 확인:

![키 파일 생성 확인](screenshots/10_key_file_check.png)

원문 증거 로그:

- `evidence/10_key_file_check.txt`
