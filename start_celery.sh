#!/bin/bash
#
# Start Celery Worker and Beat for Enterprise CRM
#

set -e

echo "=€ Starting Celery Workers..."

# Default configuration
WORKERS=${CELERY_WORKERS:-4}
LOG_LEVEL=${CELERY_LOG_LEVEL:-info}
QUEUE=${CELERY_QUEUE:-default}

# Start Celery worker
celery -A app.core.celery_app worker \
    --loglevel=$LOG_LEVEL \
    --concurrency=$WORKERS \
    --queues=$QUEUE \
    --pool=prefork \
    --max-tasks-per-child=1000 \
    --time-limit=3600 \
    --soft-time-limit=3000 \
    &

WORKER_PID=$!
echo " Celery worker started (PID: $WORKER_PID)"

# Start Celery Beat (scheduler)
echo "=R Starting Celery Beat..."
celery -A app.core.celery_app beat \
    --loglevel=$LOG_LEVEL \
    --pidfile=/tmp/celerybeat.pid \
    &

BEAT_PID=$!
echo " Celery beat started (PID: $BEAT_PID)"

# Handle shutdown gracefully
trap "echo 'ù  Shutting down Celery...'; kill $WORKER_PID $BEAT_PID; exit 0" SIGINT SIGTERM

# Wait for processes
wait
