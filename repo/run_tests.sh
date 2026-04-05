#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ENV_FILE="$ROOT_DIR/.compose.test.env"
TEST_DB_NAME="nutrideclare_test"
COMPOSE_PROJECT_NAME="nutrideclare-tests"
COMPOSE_FILES=(
  -f "$ROOT_DIR/docker-compose.test.yml"
)

ENV_FILE="$DEFAULT_ENV_FILE"

if [[ ! -f "$ENV_FILE" ]]; then
  printf 'Compose environment file not found: %s\n' "$ENV_FILE" >&2
  exit 1
fi

read_env_value() {
  python3 - "$ENV_FILE" "$1" <<'PY'
import sys
from pathlib import Path

env_path = Path(sys.argv[1])
target_key = sys.argv[2]

for raw_line in env_path.read_text().splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    if key == target_key:
        print(value)
        break
else:
    raise SystemExit(f"Missing required key: {target_key}")
PY
}

POSTGRES_USER="$(read_env_value POSTGRES_USER)"
POSTGRES_PASSWORD="$(read_env_value POSTGRES_PASSWORD)"
POSTGRES_PASSWORD_URLENCODED="$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$POSTGRES_PASSWORD")"

docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" down -v --remove-orphans >/dev/null 2>&1 || true

docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" up -d postgres

docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" build backend

docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" run --rm \
  -v "$ROOT_DIR:/workspace" \
  -e TEST_DB_NAME="$TEST_DB_NAME" \
  -e TEST_DB_USER="$POSTGRES_USER" \
  -e TEST_DB_PASSWORD="$POSTGRES_PASSWORD" \
  -e DATABASE_URL="postgresql+psycopg://$POSTGRES_USER:$POSTGRES_PASSWORD_URLENCODED@postgres:5432/$TEST_DB_NAME" \
  -e STORAGE_ROOT="/tmp/nutrideclare-test-storage" \
  backend sh -c '
    python - <<"PY"
import os
from psycopg import connect
db_name = os.environ["TEST_DB_NAME"]
conn = connect(
    dbname="postgres",
    user=os.environ["TEST_DB_USER"],
    password=os.environ["TEST_DB_PASSWORD"],
    host="postgres",
    port=5432,
    autocommit=True,
)
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cur.fetchone()
    if exists:
        cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()", (db_name,))
        cur.execute(f"DROP DATABASE {db_name}")
    cur.execute(f"CREATE DATABASE {db_name}")
conn.close()
PY
    PYTHONPATH=/app:/workspace/backend pytest /workspace/unit_tests /workspace/API_tests -q
  '
