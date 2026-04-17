#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$ROOT_DIR/.compose.env"

if [[ ! -f "$ENV_FILE" ]]; then
  printf 'No .compose.env found. Bootstrapping randomized local secrets via init-db.sh\n'
  "$ROOT_DIR/init-db.sh" "$@"
fi

docker compose -f "$ROOT_DIR/docker-compose.yml" up --build
