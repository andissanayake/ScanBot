# Use node image for development
FROM node:18

# Set the working directory
WORKDIR /app

# Copy the package.json and package-lock.json (if it exists) to install dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the development server port (change to 3000 if needed)
EXPOSE 1000

# Start the Vite development server
CMD ["npm", "run", "dev"]
