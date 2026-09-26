#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-atuf-book-lab}"
python3 setup.py
