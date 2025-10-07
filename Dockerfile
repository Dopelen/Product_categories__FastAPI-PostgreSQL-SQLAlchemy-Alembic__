# Используем официальный Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем файлы Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry и зависимости проекта
RUN pip install --no-cache-dir poetry==1.7.1 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Копируем весь проект
COPY . .

# Порт приложения
EXPOSE 8000

# Команда запуска (только FastAPI, миграции вручную)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]