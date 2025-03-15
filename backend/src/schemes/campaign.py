from typing import Annotated

from pydantic import BaseModel, Field, model_validator, computed_field

from ..config import config
from ..core.utils import undefined
from ..models.campaign import Campaign
from src.enums import FULL_GENDER, AD_TEXT_SIZE
from .shared import AdvertiserID, CampaignID, ClientID


__all__ = ("BaseCampaignDTO", "CampaignDTO", "CampaignTargetDTO", "EditCampaignRequestPatch",
           "GetCampaignsResponse", "AdvertDTO", "ClickAdvertRequest",
           "GenerateAdvertRequest", "GenerateAdvertResponse")



CostPerImpression = Annotated[float, Field(description="Стоимость показа", ge=0, examples=[10])]
CostPerClick = Annotated[float, Field(description="Стоимость клика", ge=0, examples=[100])]
AdTitle = Annotated[str, Field(description="Заголовок рекламной кампании", examples=["Red Apple"])]
AdText = Annotated[str, Field(description="Текст рекламной кампании", examples=["Best offer!"])]
AdImageID = Annotated[str, Field(description="ID изображения (получить в /files)", examples=["ffda9bd7-39b3-4b5e-9f82-993e869b2e4d.jpeg"], default=None)]
ImpressionsLimit = Annotated[int, Field(description="Лимит показов", ge=0, examples=[1000])]
ClicksLimit = Annotated[int, Field(description="Лимит переходов (не может быть больше лимита показов)", ge=0, examples=[100])]
StartDate = Annotated[int, Field(description="Дата начала кампании в днях (включительно)", examples=[15])]
EndDate = Annotated[int, Field(description="Дата окончания кампании в днях (включительно, не может быть меньше start_date)", examples=[30])]

class CampaignTargetDTO(BaseModel):
    gender: FULL_GENDER | None = Field(description="Пол клиента", default=None)
    age_from: int | None = Field(description="Минимальный возраст клиента", ge=0, examples=[18], default=None)
    age_to: int | None = Field(description="Максимальный возраст клиента (не может быть меньше age_from)", ge=0, examples=[18], default=None)
    location: str | None = Field(description="Локация клиента", examples=["Moscow"], default=None)

    @model_validator(mode = "after")
    def validate_dates(self):
        if self.age_to and self.age_from and self.age_to < self.age_from:
            raise ValueError("age_to should be greater than age_from")
        return self

class BaseCampaignDTO(BaseModel):
    impressions_limit: ImpressionsLimit
    clicks_limit: ClicksLimit
    cost_per_impression: CostPerImpression
    cost_per_click: CostPerClick
    ad_title: AdTitle
    ad_text: AdText
    ad_image_id: AdImageID | None = Field(default=None)
    start_date: StartDate
    end_date: EndDate
    targeting: CampaignTargetDTO = Field(default=CampaignTargetDTO())

    @model_validator(mode = "after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date should be greater than start_date")
        return self

    @model_validator(mode="after")
    def validate_limits(self):
        if self.clicks_limit > self.impressions_limit:
            raise ValueError("clicks_limit cannot be greater than impressions_limit")
        return self

class CampaignDTO(BaseCampaignDTO):
    campaign_id: CampaignID
    advertiser_id: AdvertiserID

    @computed_field
    @property
    def ad_image_url(self) -> str | None:
        if not self.ad_image_id: return None
        return config.api_url + "/files/" + self.ad_image_id

    @classmethod
    def from_db(cls, campaign: Campaign):
        model_dump = campaign.model_dump()
        return CampaignDTO(
            **model_dump,
            targeting = CampaignTargetDTO(
                **{
                    k.removeprefix("target_"): v
                    for k, v in model_dump.items()
                    if k.startswith("target_")
                } # Достаём ключи вида target_ и помещаем в модель таргета
            )
        )

class EditCampaignRequestPatch(BaseModel):
    start_date: StartDate = Field(default=undefined)
    end_date: EndDate = Field(default=undefined)
    impressions_limit: ImpressionsLimit = Field(default=undefined)
    clicks_limit: ClicksLimit = Field(default=undefined)
    cost_per_impression: CostPerImpression = Field(default=undefined)
    cost_per_click: CostPerClick = Field(default=undefined)
    ad_title: AdTitle = Field(default=undefined)
    ad_text: AdText = Field(default=undefined)
    ad_image_id: AdImageID | None = Field(default=undefined)
    targeting: CampaignTargetDTO | None = Field(default=undefined)

class GetCampaignsResponse(BaseModel):
    total_pages: int = Field(description="Общее кол-во страниц с кампаниями")
    current_page: int = Field(description="Текущая страница")
    campaigns: list[CampaignDTO]

class AdvertDTO(BaseModel):
    ad_id: CampaignID
    ad_title: AdTitle
    ad_text: AdText
    ad_image_id: AdImageID | None
    advertiser_id: AdvertiserID

    @computed_field
    @property
    def ad_image_url(self) -> str | None:
        if not self.ad_image_id: return None
        return config.api_url + "/files/" + self.ad_image_id

class ClickAdvertRequest(BaseModel):
    client_id: ClientID

class GenerateAdvertRequest(BaseModel):
    ad_title: AdTitle
    size: AD_TEXT_SIZE = Field(description="Размер сгенерированного текста", default="medium")

class GenerateAdvertResponse(BaseModel):
    ad_text: AdText
