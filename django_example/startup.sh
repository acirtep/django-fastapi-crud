#!/bin/sh
set -e

python manage.py migrate
python manage.py initial_load_writers
python manage.py initial_load_articles

python manage.py runserver 0.0.0.0:8080
