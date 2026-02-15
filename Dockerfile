FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    API_URL="http://localhost:8000"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY backend ./backend
COPY frontend_js ./frontend_js
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Expose ports (Fly.io typically only exposes one public port, but we might need to proxy or run on different ports if using a custom config)
# Standard Fly setup maps 80/443 to internal_port in fly.toml. 
# Since we have two services, properly we should use a reverse proxy like Nginx or Traefik, 
# or use Streamlit as the main entrypoint and have it talk to localhost backend.
# For simplicity in this pet project, we run both. Fly will healthcheck one.
EXPOSE 8000 8501

CMD ["./start.sh"]
