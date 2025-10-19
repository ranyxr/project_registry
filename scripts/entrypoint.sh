#!/usr/bin/env bash
set -euo pipefail

if [ -f uv.lock ]; then
  uv sync --frozen
else
  uv sync
fi

uv run alembic upgrade head
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
