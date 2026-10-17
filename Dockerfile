FROM python:3.12-slim

WORKDIR /app

# сначала зависимости: так Docker кэширует этот слой и пересобирает быстрее
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# при старте применяем миграции и запускаем сервер
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]