#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Force migrations to run
python manage.py makemigrations accounts
python manage.py migrate --no-input

# Run the admin creation script
python create_admin.py