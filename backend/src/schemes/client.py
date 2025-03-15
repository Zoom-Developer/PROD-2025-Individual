from uuid import UUID

from pydantic import BaseModel, Field

from src.enums import GENDER
from .shared import ClientID


__all__ = ("ClientDTO",)


class ClientDTO(BaseModel):
    client_id: ClientID
    login: str = Field(description="Логин клиента, требует уникальности", examples=["zoomdevs"])
    age: int = Field(description="Возраст клиента", ge=0, examples=[18])
    location: str = Field(description="Локация клиента", examples=["Moscow"])
    gender: GENDER = Field(description="Пол клиента")