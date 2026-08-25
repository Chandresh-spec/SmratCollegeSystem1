#!/usr/bin/env bash
set -e

echo "=== Starting Smart College System on AWS ==="

# Run database migrations
echo "Applying database migrations..."
python Home/manage.py makemigrations --no-input || true
python Home/manage.py migrate --no-input

# Collect static files for WhiteNoise
echo "Collecting static files..."
python Home/manage.py collectstatic --no-input

echo "=== Initialization complete. Launching server... ==="

# Execute passed command
exec "$@"
