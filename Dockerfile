FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download MovieLens dataset if not present
RUN if [ ! -f "ml-100k/u.data" ]; then \
        wget -O ml-100k.zip http://files.grouplens.org/datasets/movielens/ml-100k.zip && \
        unzip ml-100k.zip && \
        mv ml-100k/* ./ml-100k/ 2>/dev/null || true && \
        rm -f ml-100k.zip; \
    fi

# Expose port
EXPOSE 8000

# Start the application
CMD ["python", "run_app.py"]
