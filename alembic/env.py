import sys
import os
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

# добавляем путь к app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import config  # config.py с DATABASE_URL
from app.models import Base  # Base с моделями SQLAlchemy

# Alembic Config object
alembic_config = context.config

# Настройка логирования
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# Используем DATABASE_URL из config.py
SQLALCHEMY_DATABASE_URL = config.DATABASE_URL
alembic_config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Метаданные моделей
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
