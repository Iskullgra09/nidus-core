#!/bin/sh
set -e

cd /app/backend

echo "Waiting for database..."
python - <<'PY'
import os
import time
import socket

host = os.environ.get("POSTGRES_SERVER", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))

for attempt in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit(f"Database not reachable at {host}:{port}")
PY

echo "Running migrations..."
alembic upgrade head

if [ "${SEED_DEMO:-false}" = "true" ]; then
  echo "Seeding demo data (SEED_DEMO=true)..."
  python seed.py
fi

echo "Starting API..."
exec "$@"
