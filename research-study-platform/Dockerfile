FROM node:18-alpine

WORKDIR /app

# Copy frontend package files
COPY research-study-platform/frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY research-study-platform/frontend/ ./

# Build the app
RUN npm run build

# Install serve
RUN npm install -g serve

EXPOSE $PORT

CMD ["sh", "-c", "serve -s build -l $PORT"]