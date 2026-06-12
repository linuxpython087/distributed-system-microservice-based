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
COPY /order_service/requirements.txt .

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
# RUN useradd -m appuser

RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g 10001 -m -s /bin/bash appuser



WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY order_service /app/order_service

COPY entrypoint.sh /entrypoint.sh

#  Permissions (script must be executable)
# RUN chmod +x /entrypoint.sh && \
#     chown -R appuser:appuser /app

RUN chmod +x /entrypoint.sh && \
    chown -R 10001:10001 /app && \
    chown 10001:10001 /entrypoint.sh



# USER appuser
USER 10001:10001

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]