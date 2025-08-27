# Stage 1: Build the application
FROM node:18 AS build

# Set the working directory
WORKDIR /app

# Copy package.json
COPY package.json ./

# Clear npm cache and install dependencies
RUN npm cache clean --force
RUN npm install

# Copy the rest of the application code
COPY . .

# Set build-time environment variables
ENV VITE_BACKEND_URL=http://localhost:8000
ENV VITE_GOOGLE_CLIENT_ID=443599365399-ahk30e024d6v8rnut75r0m8vj700vetq.apps.googleusercontent.com

# Build the application
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:alpine

# Copy the built files from the previous stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
