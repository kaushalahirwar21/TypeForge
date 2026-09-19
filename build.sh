#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Collect static files with WhiteNoise compression
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Seed complete pedagogical touch typing curriculum (idempotent)
python manage.py seed_curriculum
