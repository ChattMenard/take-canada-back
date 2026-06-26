FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libboost-python-dev \
    libexiv2-dev \
    pkg-config \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Create data directory for SQLite database and vault
RUN mkdir -p /app/data

# Expose the local default. Railway injects PORT at runtime.
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "PORT=8000 uvicorn app.main:app --host 0.0.0.0 --port 8000"]
