#!/bin/bash

# Kill any existing Django processes on port 8000
lsof -ti:8000 | xargs -r kill -9

# Start Django server on port 8000
echo "Starting Django server on port 8000..."
python manage.py runserver 8000