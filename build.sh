#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running migrations..."
python manage.py migrate

if [ -f "store/management/commands/seed_data.py" ]; then
    echo "Seeding initial data..."
    python manage.py seed_data || echo "Seeding skipped or failed"
fi

echo "Build process completed!"
