#!/bin/sh
set -eu
python manage.py migrate --noinput
exec gunicorn carhaven.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60 --access-logfile - --error-logfile -
