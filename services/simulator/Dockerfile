# Stage 1: Build & compilation environment
FROM python:3.11-slim AS builder
WORKDIR /build

# Install requirements to an isolated system location
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Minimalist Production Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app

# Copy only the compiled packages from the builder stage
COPY --from=builder /install /usr/local
COPY services/simulator/driver_producer.py .

# Force Python's console logs to stream instantly to cloud log outputs
ENV PYTHONUNBUFFERED=1

CMD ["python", "driver_producer.py"]