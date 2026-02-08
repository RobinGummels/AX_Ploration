FROM node:20-alpine AS frontend-build

WORKDIR /app/alkis-frontend

COPY alkis-frontend/package.json alkis-frontend/package-lock.json ./
RUN npm ci

COPY alkis-frontend ./

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend assets
COPY --from=frontend-build /app/alkis-frontend/dist /app/frontend/dist

# Supervisor config for running frontend + backend
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV FRONTEND_PORT=5173

# Expose API and frontend ports
EXPOSE 8000 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1

# Start both API and frontend via supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
