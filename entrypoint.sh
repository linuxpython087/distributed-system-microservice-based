#!/usr/bin/env sh
set -e

echo "Starting app (ENV=$APP_ENV)...."

export PYTHONPATH=/app




echo "Waiting for database..."
until pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_NAME; do 
sleep 2
done

echo "Running migrations (alembic)..."

cd /app/order_service && alembic upgrade head

echo "Creating kafka topics..."


echo "Starting FastAPI..."

exec uvicorn order_service.src.interfaces.api.app:app \
  --host 0.0.0.0 \
  --port 8000