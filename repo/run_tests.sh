#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEST_DB_NAME="nutrideclare_test"
COMPOSE_PROJECT_NAME="nutrideclare-tests"
COMPOSE_FILES=(-f "$ROOT_DIR/docker-compose.test.yml")
FRONTEND_TEST_IMAGE="node:22-alpine"

cleanup() {
  docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

printf '\n[run_tests] starting isolated test postgres\n'
docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" up -d postgres

printf '\n[run_tests] building backend test image\n'
docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" build backend

printf '\n[run_tests] running backend unit + API tests inside the backend container\n'
docker compose -p "$COMPOSE_PROJECT_NAME" "${COMPOSE_FILES[@]}" run --rm \
  -v "$ROOT_DIR:/workspace" \
  -e TEST_DB_NAME="$TEST_DB_NAME" \
  -e STORAGE_ROOT="/tmp/nutrideclare-test-storage" \
  backend sh -c '
    set -eu
    python - <<"PY"
import os
from psycopg import connect

db_name = os.environ["TEST_DB_NAME"]
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
conn = connect(
    dbname="postgres",
    user=user,
    password=password,
    host="postgres",
    port=5432,
    autocommit=True,
)
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    if cur.fetchone():
        cur.execute(
            "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = %s AND pid <> pg_backend_pid()",
            (db_name,),
        )
        cur.execute(f"DROP DATABASE {db_name}")
    cur.execute(f"CREATE DATABASE {db_name}")
conn.close()
PY
    export DATABASE_URL="$(python - <<"PY"
import os, urllib.parse
user = urllib.parse.quote(os.environ["POSTGRES_USER"], safe="")
password = urllib.parse.quote(os.environ["POSTGRES_PASSWORD"], safe="")
db = os.environ["TEST_DB_NAME"]
print(f"postgresql+psycopg://{user}:{password}@postgres:5432/{db}")
PY
)"
    PYTHONPATH=/app:/workspace/backend pytest /workspace/unit_tests /workspace/API_tests -q
  '

printf '\n[run_tests] running frontend unit tests inside a disposable %s container\n' "$FRONTEND_TEST_IMAGE"
docker run --rm \
  -v "$ROOT_DIR/frontend":/workspace \
  -w /workspace \
  -e CI=true \
  "$FRONTEND_TEST_IMAGE" \
  sh -c 'npm install --no-audit --no-fund --prefer-offline && npm run test:run'

printf '\n[run_tests] all test suites passed\n'
