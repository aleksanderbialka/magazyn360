#!/bin/bash

set -e

source /var/www/magazyn360/app/magazyn360_env/bin/activate
cd /var/www/magazyn360/app/magazyn360-api/

echo "> Running migrations..."
python manage.py migrate

echo "> Collecting static files..."
python manage.py collectstatic --noinput

echo "> Starting Gunicorn..."
exec gunicorn magazyn360.wsgi:application --bind 0.0.0.0:8000
