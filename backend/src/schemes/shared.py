from typing import Annotated
from uuid import UUID

from pydantic import Field, BaseModel


__all__ = ("FindRequest", "AdvertiserID", "ClientID", "CampaignID")


class FindRequest(BaseModel):
    size: int = Field(description="Количество кампаний на странице", ge=1, examples=[10], default=10)
    page: int = Field(description="Страница (начиная с 1)", ge=1, examples=[1], default=1)

AdvertiserID = Annotated[UUID, Field(description="ID рекламодателя")]
ClientID = Annotated[UUID, Field(description="ID клиента")]
CampaignID = Annotated[UUID, Field(description="ID рекламной кампании")]