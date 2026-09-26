#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka:9092 --create --if-not-exists \
  --topic atuf.orders.v3 --partitions 3 \
  --replication-factor 1 --config retention.ms=604800000
docker compose run --rm --no-deps logstash --config.test_and_exit \
  --path.data /tmp/logstash-validation
docker compose up -d logstash
