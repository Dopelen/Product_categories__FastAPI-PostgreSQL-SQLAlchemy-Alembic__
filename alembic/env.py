import sys
import os
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# ==========================================
# Путь к app для корректных импортов
# ==========================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ==========================================
# Импорт из Pydantic config
# ==========================================
from app.config import settings
from app.models import Base

# ==========================================
# Alembic Config object
# ==========================================
alembic_config = context.config

# ==========================================
# Настройка логирования
# ==========================================
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# ==========================================
# Строка подключения из Pydantic Settings
# ==========================================
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
alembic_config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Метаданные моделей
target_metadata = Base.metadata

def run_migrations_offline() -> None:
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


def do_run_migrations(connection) -> None:
    """Helper for running migrations in 'online' mode."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode (async)."""
    connectable = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


# ==========================================
# Запуск миграций
# ==========================================
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())