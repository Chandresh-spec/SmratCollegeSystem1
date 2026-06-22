#!/usr/bin/env bash
# exit on error
set -o errexit

# Dependencies are installed by Nixpacks install phase (nixpacks.toml)
# Run Django management commands
cd Home
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input
