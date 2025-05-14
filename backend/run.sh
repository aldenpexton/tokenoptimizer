#!/bin/bash

# Check if running in development or production mode
if [ "$FLASK_ENV" = "production" ]; then
    echo "Starting TokenOptimizer API in production mode..."
    gunicorn -c gunicorn.conf.py backend.app:create_app
else
    echo "Starting TokenOptimizer API in development mode..."
    python app.py
fi 