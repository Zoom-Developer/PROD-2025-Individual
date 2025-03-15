import uuid

from exc import APIError
from .models import Advertiser, FindAdvertisers
from .core import request


async def bulk_advertiser(adv_id: str, name: str) -> Advertiser:
    data = await request(
        "/advertisers/bulk",
        "POST",
        [{
            "advertiser_id": adv_id,
            "name": name
        }]
    )
    return Advertiser(**data[0])

async def get_advertiser(adv_id: str) -> Advertiser | None:
    try:
        data = await request(f"/advertisers/{adv_id}", "GET")
        return Advertiser(**data)
    except APIError:
        return None

async def find_advertisers(page: int, size: int) -> FindAdvertisers:
    data = await request(
        f"/advertisers",
        "GET",
        params = {"page": page, "size": size}
    )
    return FindAdvertisers(**data)

async def gen_ad_text_ai(text: str, advertiser_id: str) -> str:
    data = await request(
        f"/advertisers/{advertiser_id}/campaigns/generate",
        "POST",
        {"ad_title": text, "size": "small"}
    )
    return data['ad_text']