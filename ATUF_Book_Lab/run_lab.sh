#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [ -z "${COMPOSE_PROJECT_NAME:-}" ] && [ -f .lab-project ]; then
  export COMPOSE_PROJECT_NAME="$(cat .lab-project)"
fi
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
python -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"; assert sys.prefix != sys.base_prefix, "Activate .venv first"'
# Nested book steps call python3; require both names to resolve to this venv.
python3 -c 'import sys; assert sys.prefix != sys.base_prefix, "python3 must resolve to the venv"'
wait_port() {
  python - "$1" <<'PY'
import socket,sys,time
port=int(sys.argv[1]); deadline=time.monotonic()+300
while True:
    try:
        with socket.create_connection(('127.0.0.1',port),timeout=2): break
    except OSError:
        if time.monotonic() >= deadline: raise SystemExit(f'Port {port} not ready')
        time.sleep(2)
PY
}
case "${1:-help}" in
 preflight)
  command -v docker >/dev/null
  command -v curl >/dev/null
  python - <<'PY'
import re,subprocess
s=subprocess.check_output(['curl','--version'],text=True)
v=tuple(map(int,re.search(r'curl (\d+)\.(\d+)\.(\d+)',s).groups()))
assert v >= (7,76,0), 'curl 7.76.0+ required'
PY
  docker version
  docker compose version
  docker compose config --quiet
  ;;
 install)
  bash run_lab.sh preflight
  docker compose pull
  ;;
 direct)
  bash step_01.sh
  bash step_03.sh
  if [ ! -f events.ndjson ]; then python events.py batch-a events.ndjson; fi
  python direct.py
  python verify.py --count 20 --pipeline direct-v1
  python direct.py
  python verify.py --count 20 --pipeline direct-v1
  ;;
 pipeline)
  test -f events.ndjson || { echo 'Run direct first'; exit 1; }
  bash step_09.sh
  wait_port 8080
  bash step_10.sh
  python verify.py --count 20 --pipeline lab-v1
  bash step_11.sh
  python verify.py --count 20 --pipeline lab-v1
  bash step_12.sh
  python verify.py --count 20 --pipeline lab-v1
  ;;
 telemetry)
  bash step_17.sh
  echo 'Inspect the Collector output: Synthetic pipeline check must appear; enduser.email and its value must be absent.'
  ;;
 retrieval)
  python retrieval.py
  ;;
 recovery)
  test -f events.ndjson || { echo 'Run direct and pipeline first'; exit 1; }
  test ! -e batch-b.ndjson || { echo 'Recovery batch already exists. Preserve it; see README recovery instructions.'; exit 1; }
  python verify.py --count 20 --pipeline lab-v1
  trap 'docker compose start elasticsearch logstash || true' EXIT
  bash step_13.sh
  python verify.py --count 40 --pipeline lab-v1
  trap - EXIT
  ;;
 verify)
  python verify.py --count "${2:-20}" --pipeline lab-v1
  docker compose exec -T kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:9092 --describe --group orders-lab
  ;;
 stop) docker compose stop ;;
 *) echo 'Usage: bash run_lab.sh {preflight|install|direct|pipeline|telemetry|retrieval|recovery|verify [20|40]|stop}' ;;
esac
