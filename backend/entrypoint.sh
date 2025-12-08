#!/bin/sh
set -e

# ждём базу
echo "Waiting for db..."
nc -z db 5432 -v
echo "DB is up"

# миграции
python manage.py migrate --noinput

# статика
python manage.py collectstatic --noinput

# gunicorn
gunicorn star_burger.wsgi:application --bind 0.0.0.0:8000 --workers 3
