#!/usr/bin/env bash

# cron 실행 환경에서도 앱 환경 변수를 읽는다.
if [ -f /etc/profile.d/agent-app.sh ]; then
  # shellcheck disable=SC1091
  . /etc/profile.d/agent-app.sh
fi

# 과제에서 사용하는 기본 경로를 고정한다.
AGENT_HOME=${AGENT_HOME:-/home/agent-admin/agent-app}
AGENT_PORT=${AGENT_PORT:-15034}
AGENT_LOG_DIR=${AGENT_LOG_DIR:-/var/log/agent-app}
LOG_FILE="$AGENT_LOG_DIR/monitor.log"

# 헬스 체크: 프로세스가 실행 중이어야 한다.
PIDS=$(pgrep -u agent-admin -x agent-app || true)
PID=$(printf "%s\n" "$PIDS" | tail -n 1)
if [ -z "$PID" ]; then
  echo "[ERROR] agent-app process is not running"
  exit 1
fi

# 헬스 체크: 지정 포트가 LISTEN 상태여야 한다.
if ! ss -tuln | awk -v port=":${AGENT_PORT}" '$1=="tcp" && $2=="LISTEN" && $5 ~ port "$" {found=1} END {exit !found}'; then
  echo "[ERROR] TCP ${AGENT_PORT} is not LISTEN"
  exit 1
fi

# 경고만 출력: UFW가 활성화되어 있는지 확인한다.
FIREWALL_OK="yes"
if [ -f /etc/ufw/ufw.conf ] && grep -q '^ENABLED=yes' /etc/ufw/ufw.conf; then
  FIREWALL_STATUS="[OK]"
else
  FIREWALL_OK="no"
  FIREWALL_STATUS="[WARNING] UFW is not enabled"
fi

# top 배치 모드의 두 번째 샘플에서 CPU/메모리 사용률을 수집한다.
if ! TOP_OUTPUT=$(LC_ALL=C top -bn2 -d 1 2>/dev/null); then
  echo "[ERROR] failed to collect resource data with top"
  exit 1
fi

CPU=$(printf "%s\n" "$TOP_OUTPUT" | awk -F'[, ]+' '
  /^%Cpu/ {
    for (i = 1; i <= NF; i++) {
      if ($i == "id") {
        idle = $(i - 1)
        found = 1
      }
    }
  }
  END {
    if (found) printf "%.1f", 100 - idle
    else printf "0.0"
  }
')

MEM=$(printf "%s\n" "$TOP_OUTPUT" | awk -F'[:, ]+' '
  /^[KMG]iB Mem/ {
    for (i = 1; i <= NF; i++) {
      if ($i == "total") total = $(i - 1)
      if ($i == "used") used = $(i - 1)
    }
  }
  END {
    if (total > 0) printf "%.1f", used * 100 / total
    else printf "0.0"
  }
')

# 루트 디스크 사용률을 수집한다.
DISK_USED=$(df / | awk 'NR==2 { gsub("%", "", $5); print $5 }')

# 요구된 로그 형식으로 monitor.log에 기록한다.
TS=$(date '+%Y-%m-%d %H:%M:%S')
printf '[%s] PID:%s CPU:%s%% MEM:%s%% DISK_USED:%s%%\n' "$TS" "$PID" "$CPU" "$MEM" "$DISK_USED" >> "$LOG_FILE"

echo "====== SYSTEM MONITOR RESULT ======"
echo
echo "[HEALTH CHECK]"
echo "Checking process 'agent-app'... [OK] (PID: $PID)"
echo "Checking port ${AGENT_PORT}... [OK]"
echo "Checking firewall (UFW)... $FIREWALL_STATUS"
echo
echo "[RESOURCE MONITORING]"
echo "CPU Usage : ${CPU}%"
echo "MEM Usage : ${MEM}%"
echo "DISK Used : ${DISK_USED}%"
echo

# 임계값 경고는 출력만 하고 스크립트는 중단하지 않는다.
awk -v v="$CPU" 'BEGIN { exit !(v > 20) }' && echo "[WARNING] CPU threshold exceeded (${CPU}% > 20%)"
awk -v v="$MEM" 'BEGIN { exit !(v > 10) }' && echo "[WARNING] MEM threshold exceeded (${MEM}% > 10%)"
awk -v v="$DISK_USED" 'BEGIN { exit !(v > 80) }' && echo "[WARNING] DISK threshold exceeded (${DISK_USED}% > 80%)"
[ "$FIREWALL_OK" = "no" ] && echo "[WARNING] Firewall is not active"

echo
echo "[INFO] Log appended: $LOG_FILE"
