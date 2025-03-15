from api.models import Advert
from exc import APIError
from .core import request


async def get_advert(client_id: str) -> Advert | None:
    try:
        data = await request("/ads", "GET", params={"client_id": client_id})
        return Advert(**data)
    except APIError:
        return None

async def click_ad(ad_id: str, client_id: str) -> None:
    await request(f"/ads/{ad_id}/click", "POST", json={"client_id": client_id})