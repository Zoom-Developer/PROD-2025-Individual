import uuid
from fastapi import Depends
from typing import Annotated

from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.dialects.postgresql import insert

from src.models import Advertiser, ClientAdvertiserScore
from src.core.db import SessionDep


__all__ = ("AdvertiserRepository", "AdvertiserRepoDep")

from src.schemes import AdvertiserDTO


class AdvertiserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, advertiser_id: uuid.UUID) -> Advertiser | None:
        return await self.session.scalar(
            select(Advertiser).filter(Advertiser.advertiser_id == advertiser_id)
        )

    async def get_all(self, size: int, page: int) -> tuple[list[Advertiser], int]:
        stmt = select(Advertiser).order_by(Advertiser.created_at.desc())
        total_count = await self.session.scalar(select(func.count()).select_from(stmt.subquery()))
        result = await self.session.scalars(stmt.limit(size).offset(size * page))
        return result.all(), total_count

    async def bulk_insert(self, advertisers: list[AdvertiserDTO]) -> list[Advertiser]:
        stmt = insert(Advertiser).values([advertiser.model_dump() for advertiser in advertisers])
        stmt = stmt.on_conflict_do_update(
            index_elements=["advertiser_id"],
            set_={
                "name": stmt.excluded.name
            }
        )
        await self.session.exec(stmt)
        return advertisers

    async def update_score(self, client_id: uuid.UUID, advertiser_id: uuid.UUID, score: int) -> None:
        stmt = insert(ClientAdvertiserScore).values(ClientAdvertiserScore(
            client_id=client_id,
            advertiser_id=advertiser_id,
            score=score
        ).model_dump())
        stmt = stmt.on_conflict_do_update(
            index_elements=["client_id", "advertiser_id"],
            set_={
                "score": stmt.excluded.score
            }
        )
        await self.session.exec(stmt)

def create_advertiser_repository(session: SessionDep) -> AdvertiserRepository:
    return AdvertiserRepository(session)

AdvertiserRepoDep = Annotated[AdvertiserRepository, Depends(create_advertiser_repository)]