# Stage 1: Build & compilation environment
FROM python:3.11-slim AS builder
WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Minimalist Production Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

COPY --from=builder /install /usr/local
COPY services/engine/matching_engine.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "matching_engine.py"]