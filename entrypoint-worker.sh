#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for Rabbitmq..."
while ! nc -z rabbitmq 5672; do
  sleep 1
done
echo "Rabbitmq is up and running!"

echo "Starting Gunicorn..."
exec celery -A notification_service worker --loglevel=info