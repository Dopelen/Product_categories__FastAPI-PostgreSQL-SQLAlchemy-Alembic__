import asyncio
from alembic import command
from alembic.config import Config

async def run_migrations():
    config = Config("alembic.ini")
    command.upgrade(config, "head")

if __name__ == "__main__":
    asyncio.run(run_migrations())