#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
while IFS= read -r event; do
  curl --silent --show-error --fail-with-body --retry 30 --retry-all-errors \
    --retry-delay 2 --retry-max-time 180 --connect-timeout 5 --max-time 15 http://127.0.0.1:8080/ \
    -H 'Content-Type: application/json' --data-binary "$event"
done < events.ndjson
