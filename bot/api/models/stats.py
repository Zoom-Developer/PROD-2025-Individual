from pydantic import BaseModel


class CampaignStat(BaseModel):
    impressions_count: int
    clicks_count: int
    spent_impressions: float
    spent_clicks: float
    spent_total: float
    conversion: float

class CampaignStatDay(CampaignStat):
    day: int