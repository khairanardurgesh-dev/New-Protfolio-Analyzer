#!/usr/bin/env bash

# Deployment startup script for Render
# This script ensures proper Python path and environment setup

echo "🚀 Starting Django application..."

# Set PYTHONPATH to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ensure Django settings module is set
export DJANGO_SETTINGS_MODULE="config.settings"

# Wait for database to be ready (for PostgreSQL)
echo "🗄️ Waiting for database..."
python manage.py migrate --noinput

echo "✅ Application ready! Starting Gunicorn..."

# Start Gunicorn with proper configuration
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
