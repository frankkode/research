FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy public directory first
COPY public/ ./public/

# Copy src directory
COPY src/ ./src/

# Copy other necessary files
COPY tsconfig.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Build the app
RUN npm run build

# Install serve globally
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "build", "-l", "3000"]