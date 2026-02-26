FROM node:20-slim

# Install system tools: curl + lynx for web search, python3 for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    lynx \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

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
