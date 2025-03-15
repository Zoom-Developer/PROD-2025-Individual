import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from src.core.exc import NotFoundError, ValidationError, ForbiddenError
from src.core.utils import undefined
from src.core.utils.days import get_current_day
from src.models.campaign import Campaign
from src.repo.campaign import CampaignRepository, CampaignRepoDep
from src.service.files import FilesService, FilesServiceDep
from src.schemes import BaseCampaignDTO, CampaignTargetDTO

__all__ = ("CampaignService", "CampaignServiceDep")

from src.service.gpt import GPTService, GPTServiceDep


class CampaignService:

    def __init__(self, repo: CampaignRepository, gpt: GPTService, file_service: FilesService):
        self.repo = repo
        self.gpt = gpt
        self.file_service = file_service

    async def is_viewed_by_client(self, client_id: uuid.UUID, campaign_id: uuid.UUID) -> bool:
        return await self.repo.is_viewed_by_client(client_id, campaign_id)

    async def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        return await self.repo.get_by_id(campaign_id)

    async def get_by_advertiser(self, advertiser_id: uuid.UUID, size: int, page: int) -> tuple[list[Campaign], int]:
        return await self.repo.get_by_advertiser(advertiser_id, size, page)

    async def get_client_ad(self, client_id: uuid.UUID) -> Campaign | None:
        return await self.repo.get_client_ad(client_id)

    async def get_stat_by_campaign(self, campaign_id: uuid.UUID):
        return await self.repo.get_stat_by_campaign(campaign_id)

    async def get_stat_by_advertiser(self, advertiser_id: uuid.UUID):
        return await self.repo.get_stat_by_advertiser(advertiser_id)

    async def get_stat_by_advertiser_day(self, advertiser_id: uuid.UUID):
        return await self.repo.get_stat_by_advertiser_day(advertiser_id)

    async def get_stat_by_campaign_day(self, campaign_id: uuid.UUID):
        return await self.repo.get_stat_by_campaign_day(campaign_id)

    async def insert_ad_click(self, client_id: uuid.UUID, campaign: Campaign) -> None:
        if not await self.is_viewed_by_client(client_id, campaign.campaign_id):
            return
        return await self.repo.insert_ad_click(client_id, campaign)

    async def insert(self, advertiser_id: uuid.UUID, campaign: BaseCampaignDTO) -> Campaign:
        if await get_current_day() > campaign.start_date:
            raise ValidationError("start_date cannot be in the past")
        if campaign.ad_image_id and not await self.file_service.is_file_exists(campaign.ad_image_id):
            raise ValidationError("Invalid Image ID")
        if not await self.gpt.censor_text(campaign.ad_text):
            raise ForbiddenError("Text is not ethical")
        if not await self.gpt.censor_text(campaign.ad_title):
            raise ForbiddenError("Title is not ethical")
        model_dump = campaign.model_dump()
        model_dump['cost_per_click'] = Decimal(model_dump['cost_per_click'])
        model_dump['cost_per_impression'] = Decimal(model_dump['cost_per_impression'])
        try:
            return await self.repo.insert(Campaign(
                advertiser_id = advertiser_id,
                **model_dump,
                **{"target_" + k: v for k, v in model_dump['targeting'].items()} # Преобразуем модель targeting в поля target_NAME для хранения в бд
            ))
        except IntegrityError:
            raise NotFoundError("Advertiser not found")

    async def delete(self, campaign: Campaign) -> None:
        await self.repo.delete(campaign)

    async def update(self, campaign: Campaign, data: BaseCampaignDTO) -> None:
        now = await get_current_day()
        if now > campaign.end_date:
            raise ForbiddenError("Campaign has already ended")
        for k, v in data.__dict__.items():
            if v is not undefined:
                if k == "targeting":
                    if v is None:
                        v = CampaignTargetDTO()
                    for target_k, target_v in v.__dict__.items():
                        setattr(campaign, f"target_{target_k}", target_v)
                else:

                    if v == getattr(campaign, k):
                        continue
                    if k in ["impressions_limit", "clicks_limit", "start_date", "end_date"] \
                            and now >= campaign.start_date:
                        raise ForbiddenError("Campaign has already started")
                    if v and (k == "ad_image_id" and not await self.file_service.is_file_exists(v)):
                        raise ValidationError("Invalid Image ID")
                    if k == "ad_text" and not await self.gpt.censor_text(v):
                        raise ForbiddenError("Text is not ethical")
                    if k == "ad_title" and not await self.gpt.censor_text(v):
                        raise ForbiddenError("Title is not ethical")
                    if k == "start_date" and v < now:
                        raise ValidationError("start_date can not be in the past")
                    if k == "end_date" and v < campaign.start_date:
                        raise ValidationError("end_date cannot be smaller than start_date")
                    if ((k == "clicks_limit" and v > campaign.impressions_limit)
                            or (k == "impressions_limit" and v < campaign.clicks_limit)):
                        raise ValidationError("clicks_limit cannot be greater than impressions_limit")
                    if isinstance(getattr(campaign, k), Decimal):
                        v = Decimal(v)
                    setattr(campaign, k, v)

def create_campaign_service(repo: CampaignRepoDep, gpt: GPTServiceDep, file_service: FilesServiceDep) -> CampaignService:
    return CampaignService(repo, gpt, file_service)

CampaignServiceDep = Annotated[CampaignService, Depends(create_campaign_service)]