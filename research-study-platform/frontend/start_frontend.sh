#!/bin/bash

# Kill any existing React processes on port 3000
lsof -ti:3000 | xargs -r kill -9

# Start React frontend on port 3000
echo "Starting React frontend on port 3000..."
npm start