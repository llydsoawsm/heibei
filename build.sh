#!/usr/bin/env bash
# exit on error
set -o errexit

# Specify Python version
export PYTHON_VERSION=3.11.8

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate 