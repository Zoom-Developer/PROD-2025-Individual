import uuid

from fastapi import Depends

from src.core.exc import NotFoundError
from src.models.campaign import Campaign
from src.repo.campaign import CampaignRepoDep


async def get_ad(campaign_id: uuid.UUID, repo: CampaignRepoDep) -> Campaign:
    campaign = await repo.get_by_id(campaign_id)
    if not campaign:
        raise NotFoundError
    return campaign

async def get_campaign(advertiser_id: uuid.UUID, campaign: Campaign = Depends(get_ad)) -> Campaign:
    if advertiser_id != campaign.advertiser_id:
        raise NotFoundError
    return campaign