#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
python3 - <<'PY' > keyed.txt
import json
for line in open('events.ndjson'):
    x = json.loads(line)
    print(x['order_id'] + '|' + json.dumps(x))
PY
docker compose exec -T kafka /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server kafka:9092 --topic atuf.orders.v3 \
  --property parse.key=true --property 'key.separator=|' \
  --producer-property acks=all < keyed.txt
docker compose exec -T kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 --describe --group orders-lab
