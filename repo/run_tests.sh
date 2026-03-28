#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

docker compose up -d postgres

docker compose run --rm \
  -v "$ROOT_DIR:/workspace" \
  -e DATABASE_URL="postgresql+psycopg://nutrideclare:nutrideclare@postgres:5432/nutrideclare_test" \
  -e STORAGE_ROOT="/tmp/nutrideclare-test-storage" \
  backend sh -c '
    python - <<"PY"
from psycopg import connect
conn = connect("dbname=postgres user=nutrideclare password=nutrideclare host=postgres port=5432", autocommit=True)
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("nutrideclare_test",))
    exists = cur.fetchone()
    if exists:
        cur.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid()", ("nutrideclare_test",))
        cur.execute("DROP DATABASE nutrideclare_test")
    cur.execute("CREATE DATABASE nutrideclare_test")
conn.close()
PY
    PYTHONPATH=/app:/workspace/backend pytest /workspace/unit_tests /workspace/API_tests -q
  '
