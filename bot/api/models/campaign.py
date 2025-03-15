from pydantic import BaseModel

from shared import FULL_GENDER


class CampaignTarget(BaseModel):
    gender: FULL_GENDER | None
    age_from: int | None
    age_to: int | None
    location: str | None

class BaseCampaign(BaseModel):
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: float
    cost_per_click: float
    ad_title: str
    ad_text: str
    ad_image_id: str | None
    start_date: int
    end_date: int
    targeting: CampaignTarget

class Campaign(BaseCampaign):
    campaign_id: str
    advertiser_id: str
    ad_image_url: str | None

class FindCampaigns(BaseModel):
    total_pages: int
    current_page: int
    campaigns: list[Campaign]