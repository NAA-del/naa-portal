#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# This creates the instructions for the database
python manage.py makemigrations accounts
python manage.py makemigrations

# This actually creates the tables in PostgreSQL
python manage.py migrate --no-input

# This creates your admin user
python create_admin.py