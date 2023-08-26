#!/bin/ash

echo "Apply database migrations"
python manage.py migrate --no-input

echo "Collect static files"
python manage.py collectstatic --no-input

exec "$@"
