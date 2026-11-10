#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo 'Dashboard local: http://127.0.0.1:8000'
exec .venv/bin/python -m uvicorn graphpath_v2.api:app --host 127.0.0.1 --port 8000
