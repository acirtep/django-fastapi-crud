#!/bin/sh
set -e

alembic upgrade head

uvicorn mysite.main:app --host 0.0.0.0 --port 8000 --reload --log-level="debug"
