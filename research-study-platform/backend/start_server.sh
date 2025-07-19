#!/bin/bash

# Kill any existing Django processes on port 8001
lsof -ti:8001 | xargs -r kill -9

# Start Django server on port 8001
echo "Starting Django server on port 8001..."
python manage.py runserver 8001