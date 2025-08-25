FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

# Create required directories
RUN mkdir -p logs data/sandbox

# Expose port
EXPOSE 8000

CMD ["python", "src/main.py"]
