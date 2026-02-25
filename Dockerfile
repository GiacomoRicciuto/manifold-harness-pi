FROM node:20-slim

# Install pi-coding-agent globally
RUN npm install -g @mariozechner/pi-coding-agent

WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json* ./
RUN npm install --production

# Copy everything
COPY . .

# Create output directory
RUN mkdir -p /app/generations

EXPOSE 8000

CMD ["node", "api/server.mjs"]
