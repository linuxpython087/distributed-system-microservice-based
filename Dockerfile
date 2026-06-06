# -------- STAGE 1: BUILDER --------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies (only here)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


# Copy only requirements first (for caching)
COPY requirements.txt .

# Install dependencies into a separate folder
RUN pip install --prefix=/install -r requirements.txt


# -------- STAGE 2: RUNTIME --------
FROM python:3.12-slim

# Metadata
LABEL maintainer="jamestchalim12@gmail.com"

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

    
LABEL version="1.0"
LABEL description="Distibuted system"

# Build args
ARG APP_ENV=production

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=${APP_ENV}

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY . .

#  Add entrypoint script
COPY entrypoint.sh /entrypoint.sh

#  Permissions (script must be executable)
RUN chmod +x /entrypoint.sh && \
    chown -R appuser:appuser /app



USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]