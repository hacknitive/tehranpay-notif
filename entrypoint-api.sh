#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for Rabbitmq..."
while ! nc -z rabbitmq 5672; do
  sleep 1
done
echo "Rabbitmq is up and running!"

echo "Waiting for Redis..."
while ! nc -z notifredis 6380; do
  sleep 1
done
echo "Redis is up and running!"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn notification_service.wsgi:application --bind 0.0.0.0:8001