import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, text
from sqlmodel import SQLModel, Field


__all__ = ("Advertiser",)


class Advertiser(SQLModel, table=True):
    __tablename__ = "advertisers"

    advertiser_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str

    created_at: datetime = Field(sa_type=TIMESTAMP(True), sa_column_kwargs={"server_default": text("now()")})