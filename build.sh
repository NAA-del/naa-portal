#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input 

# This actually creates the tables in PostgreSQL
python manage.py migrate --no-input
