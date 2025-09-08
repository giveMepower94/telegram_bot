from pydantic import PostgresDsn, Secret
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator


class Database:
    def __init__(self, dsn: Secret[PostgresDsn]):
        self._dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def initialize(self) -> None:
        self._pool = await asyncpg.create_pool(str(self._dsn.get_secret_value()))

    async def shutdown(self) -> None:
        if self._pool is None:
            raise Exception("Pool has not been created")
        await self._pool.close()

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.pool.PoolConnectionProxy, None]:
        if self._pool is None:
            raise Exception("Pool has not been created")

        async with self._pool.acquire() as connection:
            yield connection
