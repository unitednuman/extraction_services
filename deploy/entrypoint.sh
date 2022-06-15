#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py collectstatic --noinput
python manage.py migrate --noinput

gunicorn services.wsgi:application -w 2 -b :8000 --timeout 120 --graceful-timeout 120 --worker-class gevent
