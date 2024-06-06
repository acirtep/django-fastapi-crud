#!/bin/sh
set -e

alembic upgrade head

python mysite/utils/initial_load_local_db.py
uvicorn mysite.main:app --host 0.0.0.0 --port 8000 --reload --log-level="debug"
