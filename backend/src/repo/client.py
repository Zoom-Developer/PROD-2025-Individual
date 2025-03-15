import uuid
from fastapi import Depends
from typing import Annotated

from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.dialects.postgresql import insert

from src.models import Client
from src.core.db import SessionDep


__all__ = ("ClientRepository", "ClientRepoDep")


class ClientRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, client_id: uuid.UUID) -> Client | None:
        return await self.session.scalar(
            select(Client).filter(Client.client_id == client_id)
        )

    async def get_random(self) -> Client | None:
        return await self.session.scalar(
            select(Client).order_by(func.random()).limit(1)
        )

    async def bulk_insert(self, clients: list[Client]) -> list[Client]:
        stmt = insert(Client).values([client.model_dump() for client in clients])
        stmt = stmt.on_conflict_do_update(
            index_elements=["client_id"],
            set_={
                "login": stmt.excluded.login,
                "age": stmt.excluded.age,
                "location": stmt.excluded.location,
                "gender": stmt.excluded.gender
            }
        )
        await self.session.exec(stmt)
        return clients

def create_client_repository(session: SessionDep) -> ClientRepository:
    return ClientRepository(session)

ClientRepoDep = Annotated[ClientRepository, Depends(create_client_repository)]