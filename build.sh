#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install/upgrade system dependencies if available and python packages
pip install --upgrade pip
pip install -r requirements.txt

# Run static files collection & database migrations
python manage.py collectstatic --no-input
python manage.py migrate
