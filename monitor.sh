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

# /proc/stat을 두 번 샘플링하여 CPU 사용률을 계산한다.
read -r _ u1 n1 s1 i1 w1 irq1 sirq1 steal1 _ < /proc/stat
idle1=$((i1 + w1))
total1=$((u1 + n1 + s1 + i1 + w1 + irq1 + sirq1 + steal1))
sleep 1
read -r _ u2 n2 s2 i2 w2 irq2 sirq2 steal2 _ < /proc/stat
idle2=$((i2 + w2))
total2=$((u2 + n2 + s2 + i2 + w2 + irq2 + sirq2 + steal2))
CPU=$(awk -v dt=$((total2 - total1)) -v di=$((idle2 - idle1)) 'BEGIN { if (dt > 0) printf "%.1f", (dt - di) * 100 / dt; else printf "0.0" }')

# 메모리 사용률과 루트 디스크 사용률을 수집한다.
MEM=$(free | awk '/Mem:/ { printf "%.1f", $3 * 100 / $2 }')
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
