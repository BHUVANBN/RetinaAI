#!/bin/bash

# Exit on error
set -e

# Wait for database (if using PostgreSQL in production)
# echo "Waiting for database..."
# while ! nc -z $DB_HOST $DB_PORT; do
#   sleep 0.1
# done
# echo "Database is ready!"

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (optional)
# echo "Creating superuser..."
# python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

# Start the application
echo "Starting application..."
exec "$@"
