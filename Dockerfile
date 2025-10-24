FROM python:3.11-slim

LABEL maintainer="ahui69"
LABEL description="Mordzix AI - Advanced AI Assistant with Memory & Learning"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     g++     git     curl     tesseract-ocr     tesseract-ocr-pol     && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download pl_core_news_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/workspace /app/uploads

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3   CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "app.py", "-p", "8080", "-H", "0.0.0.0"]
