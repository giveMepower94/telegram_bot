from dataclasses import dataclass
from sqlalchemy import select
from app.infra.postgres.db import Database
from app.core.users.models import User
from sqlalchemy.dialects.postgresql import insert


@dataclass
class UserRepository:
    database: Database

    async def create_user_if_not_exists(self,
                                        user_id: int,
                                        is_waiter: bool = False) -> None:
        async with self.database.session() as session:
            insert_stmt = insert(User).values(id=user_id, is_waiter=is_waiter)
            await session.execute(insert_stmt)
            await session.commit()

    async def get_waiter_user_ids(self) -> list[int]:
        async with self.database.session() as session:
            query = select(User.id).where(User.is_waiter==True)
            return list(await session.scalars(query))
