from pydantic import BaseModel


__all__ = ("DateModel",)


class DateModel(BaseModel):
    current_date: int