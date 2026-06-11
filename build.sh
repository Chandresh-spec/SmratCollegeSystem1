#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run Django management commands
cd Home
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input
