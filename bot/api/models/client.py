from pydantic import BaseModel

from shared import GENDER


class ClientDTO(BaseModel):
    client_id: str
    login: str
    age: int
    location: str
    gender: GENDER