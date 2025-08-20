# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for faster caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose port (Render sets $PORT automatically)
ENV PORT=5000

# Command to run Flask app
CMD ["python", "main.py"]