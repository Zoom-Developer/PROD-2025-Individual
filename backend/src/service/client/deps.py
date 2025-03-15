import uuid

from src.core.exc import NotFoundError
from src.models import Client
from src.repo.client import ClientRepoDep


__all__ = ("get_client",)


async def get_client(client_id: uuid.UUID, repo: ClientRepoDep) -> Client:
    client = await repo.get_by_id(client_id)
    if not client:
        raise NotFoundError
    return client