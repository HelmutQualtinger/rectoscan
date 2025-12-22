# Stage 1: Builder
FROM python:3.9-alpine as builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Create virtual environment and install packages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-alpine

# Install only runtime dependencies
RUN apk add --no-cache ca-certificates

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy application code
COPY . .

# Create upload and reordered folders
RUN mkdir -p /app/uploads /app/reordered && \
    chmod 777 /app/uploads /app/reordered

# Use non-root user
USER nobody

# Expose port 5000
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]