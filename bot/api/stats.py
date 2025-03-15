from api import request
from api.models.stats import CampaignStat, CampaignStatDay


async def get_stat_advertiser(advertiser_id: str) -> CampaignStat:
    data = await request(
        f"/stats/advertisers/{advertiser_id}/campaigns",
        "GET"
    )
    return CampaignStat(**data)

async def get_stat_advertiser_daily(advertiser_id: str) -> list[CampaignStatDay]:
    data = await request(
        f"/stats/advertisers/{advertiser_id}/campaigns/daily",
        "GET"
    )
    return [CampaignStatDay(**i) for i in data]

async def get_stat_campaign(campaign_id: str) -> CampaignStat:
    data = await request(
        f"/stats/campaigns/{campaign_id}",
        "GET"
    )
    return CampaignStat(**data)

async def get_stat_campaign_daily(campaign_id: str) -> list[CampaignStatDay]:
    data = await request(
        f"/stats/campaigns/{campaign_id}/daily",
        "GET"
    )
    return [CampaignStatDay(**i) for i in data]