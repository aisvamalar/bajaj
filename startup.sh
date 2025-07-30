#!/bin/bash

# Azure App Service startup script for RAG system

echo "Starting Bajaj RAG System deployment..."

# Create necessary directories
mkdir -p data
mkdir -p embeddings
mkdir -p metadata
mkdir -p chunks

# Install any additional dependencies if needed
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Handle potential Keras compatibility issues
pip install tf-keras || echo "tf-keras installation skipped"

# Set environment variables from Azure App Settings
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:."

# Check if NVIDIA API key is set
if [ -z "$NVIDIA_API_KEY" ]; then
    echo "Warning: NVIDIA_API_KEY not set. Please configure in Azure App Settings."
fi

echo "Starting Flask application..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 app:app
