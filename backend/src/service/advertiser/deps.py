import uuid

from src.core.exc import NotFoundError
from src.models import Advertiser
from src.repo.advertiser import AdvertiserRepoDep


__all__ = ("get_advertiser",)


async def get_advertiser(advertiser_id: uuid.UUID, repo: AdvertiserRepoDep) -> Advertiser:
    advertiser = await repo.get_by_id(advertiser_id)
    if not advertiser:
        raise NotFoundError
    return advertiser