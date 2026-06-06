#!/usr/bin/env sh
set -e

echo "Starting app (ENV=$APP_ENV)..."

export PYTHONPATH=/app

echo "Waiting for database..."
until pg_isready -h $DATABASE_HOST -p $DATABASE_PORT -U $DATABASE_NAME; do 
sleep 2
done

# simple wait
# python - << END
# import time
# import psycopg2
# import os

# host = os.getenv("DATABASE_HOST", "db")
# port = os.getenv("DATABASE_PORT", "5432")
# user = os.getenv("DATABASE_USER", "postgres")
# password = os.getenv("DATABASE_PASSWORD", "")
# db = os.getenv("DATABASE_NAME", "distributed")

# while True:
#     try:
#         conn = psycopg2.connect(
#             host=host,
#             port=port,
#             user=user,
#             password=password,
#             dbname=db,
#         )
#         conn.close()
#         print("DB is ready!")
#         break
#     except Exception as e:
#         print("DB not ready, retrying...")
#         time.sleep(2)
# END

echo "Running migrations (alembic)..."

cd /app/order_service && alembic upgrade head

echo "Starting FastAPI..."

exec uvicorn order_service.src.interfaces.api.app:app \
  --host 0.0.0.0 \
  --port 8000