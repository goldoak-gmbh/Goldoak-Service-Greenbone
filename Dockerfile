# Dockerfile for the Python Microservice
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (optional)
# RUN apt-get update && apt-get install -y build-essential

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port for FastAPI
EXPOSE 8000

# Run uvicorn to serve the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



