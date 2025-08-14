#!/bin/bash

# Install Python dependencies if not already installed
if ! command -v gunicorn &> /dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the application
echo "Starting application..."
cd backend && gunicorn --bind 0.0.0.0:${PORT:-8000} src.main:app