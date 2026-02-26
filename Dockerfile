FROM node:20-slim

# Install system tools: curl + lynx for web search, python3 + weasyprint for PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    lynx \
    python3 \
    python3-pip \
    python3-venv \
    libpango1.0-0 \
    libpangoft2-1.0-0 \
    libglib2.0-0 \
    libharfbuzz0b \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Install WeasyPrint for PDF generation
RUN pip install --break-system-packages weasyprint

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

CMD ["node", "api/startup.mjs"]
