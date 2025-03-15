import uuid

from sqlalchemy import String
from sqlmodel import SQLModel, Field

from src.enums import FULL_GENDER


__all__ = ("Client",)


class Client(SQLModel, table=True):
    __tablename__ = "clients"

    client_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    login: str
    age: int
    location: str
    gender: FULL_GENDER = Field(sa_type=String)