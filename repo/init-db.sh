#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$ROOT_DIR/.compose.env"

generate_token() {
  python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
}

generate_password() {
  python3 -c 'import secrets, string; alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"; print("".join(secrets.choice(alphabet) for _ in range(20)))'
}

generate_encryption_key() {
  python3 -c 'import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())'
}

if [[ -f "$ENV_FILE" && "${1:-}" != "--force" ]]; then
  printf 'Using existing bootstrap config at %s\n' "$ENV_FILE"
  exit 0
fi

POSTGRES_PASSWORD="$(generate_password)"
JWT_SECRET_KEY="$(generate_token)"
JWT_REFRESH_SECRET_KEY="$(generate_token)"
REFRESH_TOKEN_PEPPER="$(generate_token)"
ENCRYPTION_KEY="$(generate_encryption_key)"
DB_ENCRYPTION_KEY="$(generate_token)"
CAPTCHA_SECRET="$(generate_token)"
SEED_PARTICIPANT_PASSWORD="$(generate_password)"
SEED_REVIEWER_PASSWORD="$(generate_password)"
SEED_ADMIN_PASSWORD="$(generate_password)"

cat > "$ENV_FILE" <<EOF
POSTGRES_DB=nutrideclare
POSTGRES_USER=nutrideclare
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY=$JWT_REFRESH_SECRET_KEY
REFRESH_TOKEN_PEPPER=$REFRESH_TOKEN_PEPPER
ENCRYPTION_KEY=$ENCRYPTION_KEY
DB_ENCRYPTION_KEY=$DB_ENCRYPTION_KEY
CAPTCHA_SECRET=$CAPTCHA_SECRET
SEED_PARTICIPANT_USERNAME=participant_demo
SEED_PARTICIPANT_PASSWORD=$SEED_PARTICIPANT_PASSWORD
SEED_REVIEWER_USERNAME=reviewer_demo
SEED_REVIEWER_PASSWORD=$SEED_REVIEWER_PASSWORD
SEED_ADMIN_USERNAME=admin_demo
SEED_ADMIN_PASSWORD=$SEED_ADMIN_PASSWORD
EOF

chmod 600 "$ENV_FILE"

printf 'Wrote bootstrap config to %s\n' "$ENV_FILE"
printf 'Participant login: participant_demo / %s\n' "$SEED_PARTICIPANT_PASSWORD"
printf 'Reviewer login: reviewer_demo / %s\n' "$SEED_REVIEWER_PASSWORD"
printf 'Administrator login: admin_demo / %s\n' "$SEED_ADMIN_PASSWORD"
