#!/usr/bin/env bash
set -e  # Exit on any error

# Set PYTHONPATH to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🔧 Installing dependencies..."
pip install -r requirements_prod.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗄️ Running migrations..."
python manage.py migrate

echo "✅ Build completed successfully!"
