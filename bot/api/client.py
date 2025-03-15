from api.models import ClientDTO
from exc import APIError
from .core import request


async def register_client(req: ClientDTO) -> ClientDTO | None:
    try:
        data = await request("/clients/bulk", "POST", json=[req.model_dump()])
        return ClientDTO(**data[0])
    except APIError:
        return None

async def get_random_client() -> ClientDTO | None:
    try:
        data = await request("/clients/random", "GET")
        return ClientDTO(**data)
    except APIError:
        return None