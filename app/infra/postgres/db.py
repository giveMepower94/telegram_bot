from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    async_sessionmaker,
                                    AsyncSession)
from sqlalchemy.orm import DeclarativeBase
from pydantic import Secret, PostgresDsn


class Database:
    def __init__(self, dsn: Secret[PostgresDsn],
                 declarative_base: type[DeclarativeBase]):
        self._engine = create_async_engine(str(dsn.get_secret_value()))
        self._async_session = async_sessionmaker(self._engine)

        self._declarative_base = declarative_base

    async def shutdown(self) -> None:
        await self._engine.dispose()

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(self._declarative_base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._async_session()

        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
