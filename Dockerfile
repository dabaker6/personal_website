# Use Python 3.13 slim image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port 80 for Azure App Service
EXPOSE 80

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:create_app()"]