#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
docker compose exec -T kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 --topic atuf.orders.v3 \
  --partition 0 --offset 0 --max-messages 3 \
  --timeout-ms 10000 > replay.ndjson
wc -l replay.ndjson
