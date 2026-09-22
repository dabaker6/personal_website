# builder
FROM python:3.13-slim AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# runtime
FROM python:3.13-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy the application code
COPY . .

RUN rm -rf /usr/local/lib/python3.*/site-packages/pip \
        /usr/local/lib/python3.*/site-packages/pip-*.dist-info \
        /opt/venv/lib/python3.*/site-packages/pip \
        /opt/venv/lib/python3.*/site-packages/pip-*.dist-info \
    && useradd -m -u 1000 appuser \
    && chown -R appuser /app

USER appuser

# Expose port 80 for Azure App Service
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
