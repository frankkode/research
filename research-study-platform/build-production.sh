#!/bin/bash
# Production build script for Railway deployment

echo "🚀 Building for production..."

# Change to frontend directory
cd frontend

# Clear any existing build
rm -rf build/
rm -rf node_modules/.cache/ 2>/dev/null

# Set production environment
export NODE_ENV=production
export REACT_APP_API_URL=https://research-production-46af.up.railway.app/api
export REACT_APP_ENVIRONMENT=production
export GENERATE_SOURCEMAP=false

# Show environment
echo "📋 Environment variables:"
env | grep REACT_APP_

# Build
npm run build

echo "✅ Production build complete!"
echo "📁 Build directory: $(pwd)/build"

# Show API configuration that will be used
echo "🔍 API URL in build: https://research-production-46af.up.railway.app/api"