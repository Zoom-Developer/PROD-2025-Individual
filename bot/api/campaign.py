from api import request
from exc import APIError
from .models import BaseCampaign, Campaign, FindCampaigns


async def create_campaign(advertiser_id: str, req: BaseCampaign) -> Campaign:
    data = await request(f"/advertisers/{advertiser_id}/campaigns", "POST", json=req.model_dump())
    return Campaign(**data)

async def get_campaign(advertiser_id: str, campaign_id: str) -> Campaign | None:
    try:
        data = await request(f"/advertisers/{advertiser_id}/campaigns/{campaign_id}", "GET")
        return Campaign(**data)
    except APIError:
        return None

async def find_campaigns(advertiser_id: str, page: int, size: int) -> FindCampaigns:
    data = await request(
        f"/advertisers/{advertiser_id}/campaigns",
        "GET",
        params = {"page": page, "size": size}
    )
    return FindCampaigns(**data)

async def delete_campaign(advertiser_id: str, campaign_id: str) -> None:
    await request(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}",
        "DELETE"
    )

async def edit_campaign(advertiser_id: str, campaign_id: str, **kwargs) -> None:
    await request(
        f"/advertisers/{advertiser_id}/campaigns/{campaign_id}",
        "PATCH",
        json=kwargs
    )