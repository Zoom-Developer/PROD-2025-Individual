from pydantic import BaseModel


__all__ = ("SecurityModeration",)


class SecurityModeration(BaseModel):
    is_enabled: bool