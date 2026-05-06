# Use slim Python base — much smaller than Railway's default Nixpacks image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for chromadb/onnxruntime
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching — only reinstalls if requirements.txt changes)
COPY requirements.txt .

# Install Python dependencies — no cache to keep image lean
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Railway injects PORT dynamically — do not hardcode
ENV PORT=8000

# Start the FastAPI server
CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT
