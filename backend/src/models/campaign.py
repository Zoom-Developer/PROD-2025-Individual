import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, TIMESTAMP, text, NUMERIC
from sqlmodel import SQLModel, Field


__all__ = ("Campaign",)

from src.enums import FULL_GENDER


class Campaign(SQLModel, table=True):
    __tablename__ = "campaigns"

    campaign_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    advertiser_id: uuid.UUID = Field(foreign_key="advertisers.advertiser_id", index=True)
    impressions_limit: int
    clicks_limit: int
    cost_per_impression: Decimal = Field(sa_type=NUMERIC(20, 2))
    cost_per_click: Decimal = Field(sa_type=NUMERIC(20, 2))
    ad_title: str
    ad_text: str
    ad_image_id: str | None
    start_date: int
    end_date: int

    target_gender: FULL_GENDER | None = Field(sa_type=String)
    target_age_from: int | None
    target_age_to: int | None
    target_location: str | None

    created_at: datetime = Field(sa_type=TIMESTAMP(True), sa_column_kwargs={"server_default": text("now()")})