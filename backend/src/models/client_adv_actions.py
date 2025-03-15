import uuid
from decimal import Decimal

from sqlalchemy import NUMERIC
from sqlmodel import SQLModel, Field


__all__ = ("ClientAdvertiserScore", "ClientViewCampaign", "ClientClickCampaign")


class ClientAdvertiserScore(SQLModel, table=True):
    __tablename__ = "client_advertiser_scores"

    client_id: uuid.UUID = Field(foreign_key="clients.client_id", primary_key=True, ondelete="CASCADE", index=True)
    advertiser_id: uuid.UUID = Field(foreign_key="advertisers.advertiser_id", primary_key=True, ondelete="CASCADE", index=True)
    score: int

class ClientViewCampaign(SQLModel, table=True):
    __tablename__ = "client_view_campaigns"

    client_id: uuid.UUID = Field(foreign_key="clients.client_id", primary_key=True, ondelete="CASCADE", index=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id", primary_key=True, ondelete="CASCADE", index=True)
    date: int
    cost: Decimal = Field(sa_type=NUMERIC(20, 2))

class ClientClickCampaign(SQLModel, table=True):
    __tablename__ = "client_click_campaigns"

    client_id: uuid.UUID = Field(foreign_key="clients.client_id", primary_key=True, ondelete="CASCADE", index=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.campaign_id", primary_key=True, ondelete="CASCADE", index=True)
    date: int
    cost: Decimal = Field(sa_type=NUMERIC(20, 2))