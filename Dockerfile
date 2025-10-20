FROM python:3.11-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем Poetry и зависимости (без виртуального окружения)
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Копируем исходный код и миграции
COPY app/ ./app
COPY alembic/ ./alembic/
COPY alembic.ini .

# Команда запуска: применяем миграции и стартуем приложение
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]