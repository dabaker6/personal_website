# ---- builder ----
FROM python:3.13-slim AS builder
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

# ---- runtime ----
FROM gcr.io/distroless/python3-debian13:nonroot

ENV PYTHONPATH=/deps \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=builder /deps /deps
COPY . .

EXPOSE 8000
CMD ["-m", "gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
