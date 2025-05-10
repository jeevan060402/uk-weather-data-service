#!/bin/bash

set -e

# Delete this step after migrating to k8s
INFRA_MODE=${INFRA_MODE:-"CA"}

if [ "$INFRA_MODE" == "K8S" ]; then
    echo "Fetching secrets..."
    # fetch secrets from azure key vault
    python scripts/fetch_secrets.py $AZURE_KEY_VAULT $SERVICE_NAME ".env"
fi

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    # export $(grep -v '^#' .env | xargs -d '\n')
fi


# Detect CPU cores cross-platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CPU_CORES=$(grep -c ^processor /proc/cpuinfo)
elif [[ "$OSTYPE" == "darwin"* ]]; then
    CPU_CORES=$(sysctl -n hw.ncpu)
else
    CPU_CORES=1 # Default to 1 if unknown OS
fi


# Default values
PORT=8000
GUNICORN_WORKERS=${GUNICORN_WORKERS:-$((2 * CPU_CORES + 1))}
GUNICORN_THREADS_PER_WORKER=${GUNICORN_THREADS_PER_WORKER:-2}
PROJECT_ROOT_DIR=${PROJECT_ROOT_DIR:-"/project/altius"}
LOG_DIR=${LOG_DIR:-"/logs"}


# Parse named arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port=*)
            PORT="${1#*=}"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --gunicorn-workers=*)
            GUNICORN_WORKERS="${1#*=}"
            shift
            ;;
        --gunicorn-workers)
            GUNICORN_WORKERS="$2"
            shift 2
            ;;
        --gunicorn-threads-per-worker=*)
            GUNICORN_THREADS_PER_WORKER="${1#*=}"
            shift
            ;;
        --gunicorn-threads-per-worker)
            GUNICORN_THREADS_PER_WORKER="$2"
            shift 2
            ;;
        --project-root-dir=*)
            PROJECT_ROOT_DIR="${1#*=}"
            shift
            ;;
        --project-root-dir)
            PROJECT_ROOT_DIR="$2"
            shift 2
            ;;
        --log-dir=*)
            LOG_DIR="${1#*=}"
            shift
            ;;
        --log-dir)
            LOG_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--port=8000] [--gunicorn-workers=1] [--gunicorn-threads-per-worker=2] [--project-root-dir=/project] [--log-dir=/logs]"
            exit 0
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Validate Port
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -le 0 ] || [ "$PORT" -gt 65535 ]; then
    echo "Invalid port: $PORT"
    exit 1
fi


echo "Starting services with configuration:"
echo "Port: $PORT"
echo "Gunicorn workers: $GUNICORN_WORKERS"
echo "Gunicorn threads per worker: $GUNICORN_THREADS_PER_WORKER"
echo "Project root directory: $PROJECT_ROOT_DIR"
echo "Log directory: $LOG_DIR"


# CRON deployment mode
if [ "$DEPLOYMENT_MODE" == "CRON" ]; then
    echo "Scheduling Cronjobs..."
    service cron start
    cd $PROJECT_ROOT_DIR
    python manage.py crontab add
    exec tail -f ${PROJECT_ROOT_DIR}${LOG_DIR}/django.log
fi


# API deployment mode
if [ "$DEPLOYMENT_MODE" == "API" ]; then
    echo "Starting Gunicorn..."
    cd $PROJECT_ROOT_DIR
    exec gunicorn \
        --bind 0.0.0.0:$PORT \
        --workers $GUNICORN_WORKERS \
        --threads $GUNICORN_THREADS_PER_WORKER \
        --worker-class gthread \
        --timeout 0 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 200 \
        --access-logfile '-' \
        --error-logfile '-' \
        --log-level info \
        config.wsgi:application
fi


# FULL deployment mode
if [ "$DEPLOYMENT_MODE" == "FULL" ]; then
    echo "Scheduling Cronjobs..."
    service cron start
    cd $PROJECT_ROOT_DIR
    python manage.py crontab add

    echo "Starting Gunicorn..."
    exec gunicorn \
        --bind 0.0.0.0:$PORT \
        --workers $GUNICORN_WORKERS \
        --threads $GUNICORN_THREADS_PER_WORKER \
        --worker-class gthread \
        --timeout 0 \
        --graceful-timeout 30 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 200 \
        --access-logfile '-' \
        --error-logfile '-' \
        --log-level info \
        config.wsgi:application
fi
