from typing import Literal

from pydantic import BaseModel, Field

from .shared import AdvertiserID, ClientID


__all__ = ("AdvertiserDTO", "UpdateMLScoreRequest", "GetAdvertisersResponse", "UpdateMLScoreResponse")


class AdvertiserDTO(BaseModel):
    advertiser_id: AdvertiserID
    name: str = Field(description="Название рекламодателя", examples=["RaZoom Corporation"])

class UpdateMLScoreRequest(BaseModel):
    client_id: ClientID
    advertiser_id: AdvertiserID
    score: int = Field(description="Оценка релевантности рекламодателя", ge=0)

class UpdateMLScoreResponse(BaseModel):
    status: Literal['Ok'] = "Ok"

class GetAdvertisersResponse(BaseModel):
    total_pages: int = Field(description="Общее кол-во страниц с кампаниями")
    current_page: int = Field(description="Текущая страница")
    advertisers: list[AdvertiserDTO]

