# /app/db_connection.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager
from app.config import settings


# Setup database connection securely
DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")


class DatabaseSessionManager():
    def __init__(self, url):
        self._engine = create_async_engine(url, echo=True)
        self._session_factory = async_sessionmaker(self._engine)

    @asynccontextmanager
    async def session(self):
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise # Default Error
        finally:
            await session.close()

    async def close(self):
        await self._engine.dispose()

session_manager = DatabaseSessionManager(DATABASE_URL)

async def get_db():
    async with session_manager.session() as session:
        yield session