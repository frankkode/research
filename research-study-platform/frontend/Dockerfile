FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including devDependencies needed for build)
RUN npm install

# Copy all source files
COPY . .

# Build the app
RUN npm run build

# Install serve globally
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "build", "-l", "3000"]