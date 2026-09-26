#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
python3 - <<'PY'
import json
x = json.loads(open('events.ndjson').readline())
x['event_id'] = 'bad-amount'
x['amount'] = 'twenty dollars'
json.dump(x, open('bad.json', 'w'))
PY
curl --silent --show-error --fail-with-body --retry 30 --retry-all-errors \
    --retry-delay 2 --retry-max-time 180 --connect-timeout 5 --max-time 15 http://127.0.0.1:8080/ \
  -H 'Content-Type: application/json' --data-binary @bad.json
head -n 1 events.ndjson > valid.json
curl --silent --show-error --fail-with-body --retry 30 --retry-all-errors \
    --retry-delay 2 --retry-max-time 180 --connect-timeout 5 --max-time 15 http://127.0.0.1:8080/ \
  -H 'Content-Type: application/json' --data-binary @valid.json
# File output is asynchronous; allow bounded time for the fixture.
found=false
for attempt in $(seq 1 30); do
  if docker compose exec -T logstash cat \
    /usr/share/logstash/data/quarantine.ndjson | grep 'bad-amount' >/dev/null; then
    found=true
    break
  fi
  sleep 1
done
[ "$found" = true ] || { echo "Quarantine check failed" >&2; exit 1; }
