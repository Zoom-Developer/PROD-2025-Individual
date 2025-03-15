from typing import Annotated
from uuid import UUID
from fastapi import Depends

from src.models import Client
from src.repo.client import ClientRepository, ClientRepoDep
from src.schemes import ClientDTO


__all__ = ("ClientService", "ClientServiceDep")


class ClientService:

    def __init__(self, repo: ClientRepository):
        self.repo = repo

    async def get_by_id(self, client_id: UUID) -> Client | None:
        return await self.repo.get_by_id(client_id)

    async def get_random(self) -> Client | None:
        return await self.repo.get_random()

    async def bulk_insert(self, clients: list[ClientDTO]) -> list[Client]:
        return await self.repo.bulk_insert([
            Client(**client.model_dump())
            for client in clients
        ])

def create_client_service(repo: ClientRepoDep) -> ClientService:
    return ClientService(repo)

ClientServiceDep = Annotated[ClientService, Depends(create_client_service)]