#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
python3 events.py batch-a events.ndjson
python3 direct.py
curl --fail-with-body 'http://127.0.0.1:9200/atuf-orders-*/_count'
python3 direct.py
curl --fail-with-body 'http://127.0.0.1:9200/atuf-orders-*/_count'
