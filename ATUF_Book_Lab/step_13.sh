#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
docker compose stop logstash
docker compose stop elasticsearch
# Use a new batch name once; preserve this file for later retries.
python3 events.py batch-b batch-b.ndjson
python3 - <<'PYCODE' > keyed-b.txt
import json
for line in open('batch-b.ndjson', encoding='utf-8'):
    event = json.loads(line)
    print(event['order_id'] + '|' + json.dumps(event))
PYCODE
docker compose exec -T kafka /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server kafka:9092 --topic atuf.orders.v3 \
  --property parse.key=true --property 'key.separator=|' \
  --producer-property acks=all < keyed-b.txt
docker compose exec -T kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 --describe --group orders-lab
docker compose start elasticsearch
curl --fail-with-body --retry 30 --retry-all-errors \
  --retry-delay 2 --retry-max-time 120 --max-time 5 \
  http://127.0.0.1:9200/
docker compose start logstash
