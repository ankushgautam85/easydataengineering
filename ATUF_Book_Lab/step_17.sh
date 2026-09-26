#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
docker compose up -d otel
python3 telemetry.py
docker compose logs --tail=50 otel
