#!/usr/bin/env bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --no-input

# development
# python3 manage.py runserver 0.0.0.0:8000

# production
gunicorn -w 4 ChatAPI_api.wsgi:application --bind 0.0.0.0:8000 --timeout 600 -k gevent --worker-connections 1000
