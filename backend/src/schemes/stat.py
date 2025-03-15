from pydantic import BaseModel, computed_field, Field

__all__ = ("CampaignStat", "CampaignStatDay")


class CampaignStat(BaseModel):
    impressions_count: int = Field(description="Количество показов", examples=[10])
    clicks_count: int = Field(description="Количество переходов", examples=[2])
    spent_impressions: float = Field(description="Потрачено средств на показы", examples=[1500])
    spent_clicks: float = Field(description="Потрачено средств на переходы", examples=[5000])

    @computed_field(description="Соотношение переходов к показам (в %)", examples=[12])
    @property
    def conversion(self) -> float:
        if self.impressions_count == 0: return 0
        return round((self.clicks_count / self.impressions_count) * 100, 1)

    @computed_field(description="Общее кол-во потраченных средств", examples=[6500])
    @property
    def spent_total(self) -> float:
        return round(self.spent_clicks + self.spent_impressions, 2)

class CampaignStatDay(CampaignStat):
    day: int