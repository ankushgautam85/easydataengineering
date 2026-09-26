#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
docker compose config --quiet
docker compose up -d elasticsearch kafka
curl --fail-with-body --retry 30 --retry-all-errors \
  --retry-delay 2 --retry-max-time 120 --max-time 5 \
  http://127.0.0.1:9200/
ready=false
for attempt in $(seq 1 30); do
  if docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server kafka:9092 --list; then
    ready=true
    break
  fi
  sleep 2
done
[ "$ready" = true ] || { echo "Kafka not ready" >&2; exit 1; }
