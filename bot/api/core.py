from typing import Any

from aiogram.client.session import aiohttp

from config import config
from exc import APIError


async def request(endpoint: str, method: str, json: list | dict = None, data: Any = None, params: dict = None) -> dict | None:
    async with aiohttp.ClientSession() as session:
        async with session.request(method, config.api_url + endpoint, json=json, data=data, params=params) as response:
            if response.status >= 400:
                raise APIError(response.status)
            try:
                return await response.json()
            except Exception as e:
                return None