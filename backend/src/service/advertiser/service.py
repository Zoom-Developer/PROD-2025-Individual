from typing import Annotated
from uuid import UUID
from fastapi import Depends

from src.core.exc import NotFoundError
from src.models import Advertiser
from src.repo.advertiser import AdvertiserRepository, AdvertiserRepoDep


__all__ = ("AdvertiserService", "AdvertiserServiceDep")

from src.repo.client import ClientRepository, ClientRepoDep


class AdvertiserService:

    def __init__(self, repo: AdvertiserRepository, client_repo: ClientRepository):
        self.repo = repo
        self.client_repo = client_repo

    async def get_by_id(self, advertiser_id: UUID) -> Advertiser | None:
        return await self.repo.get_by_id(advertiser_id)

    async def get_all(self, size: int, page: int) -> tuple[list[Advertiser], int]:
        return await self.repo.get_all(size, page)

    async def bulk_insert(self, advertisers: list[Advertiser]) -> list[Advertiser]:
        return await self.repo.bulk_insert([
            Advertiser(**client.model_dump())
            for client in advertisers
        ])

    async def update_score(self, client_id: UUID, advertiser_id: UUID, score: int) -> None:
        client = await self.client_repo.get_by_id(client_id)
        advertiser = await self.repo.get_by_id(advertiser_id)
        if not client or not advertiser:
            raise NotFoundError
        await self.repo.update_score(client_id, advertiser_id, score)

def create_advertiser_service(repo: AdvertiserRepoDep, client_repo: ClientRepoDep) -> AdvertiserService:
    return AdvertiserService(repo, client_repo)

AdvertiserServiceDep = Annotated[AdvertiserService, Depends(create_advertiser_service)]