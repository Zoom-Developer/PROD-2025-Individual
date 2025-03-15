import time
from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient
from openai import AsyncOpenAI

from src.config import config
from src.core.utils import get_enabled_moderation
from src.enums import AD_TEXT_SIZE


class GPTService:

    client = AsyncOpenAI(
        api_key=config.openai_api_key,
        http_client=AsyncClient(proxy=config.proxy_url)
    )

    async def _generate(self, messages: list[dict], temperature: float = None) -> str:
        res = await self.client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            temperature = temperature
        )
        return res.choices[0].message.content

    async def generate_ad_text(self, ad_title: str, advertiser_title: str, size: AD_TEXT_SIZE) -> str:
        messages = [
            {
                "role": "system",
                "content": "Ты ответственный за генерирование рекламных текстов в очень крупной компании. "
                      "Твоя задача состоит в том, чтобы исходя из названия рекламной кампании "
                      "и названия рекламодателя составить описание рекламы, "
                      "которое заставит пользователя заинтересоваться. "
                      "Ты должен отвечать только рекламным текстом и ничего больше. "
                      "Есть разные степени размера текста в символах: small (50<), medium (~100), large(>100)"
            },
            {
                "role": "user",
                "content": f"Название кампании: {ad_title}\nИмя рекламодателя: {advertiser_title}\nРазмер текста: {size}"
            }
        ]
        return await self._generate(messages, 0.25)

    async def censor_text(self, text: str, force: bool = False) -> bool:
        if not force and not await get_enabled_moderation():
            return True
        messages = [
            {
                "role": "system",
                "content": "Ты проверяешь рекламу на наличие в ней матов или рекламы незаконной деятельности"
                    "Если в выданном тебе тексте таковые присутствуют, ты должен ответить true, "
                    "иначе false, любой другой ответ не допускается"
            },
            {
                "role": "user",
                "content": text
            }
        ]
        res = await self._generate(messages, 1)
        return True if "false" in res.lower() else False # инвертирование ответа

async def create_gpt_service() -> GPTService:
    return GPTService()

GPTServiceDep = Annotated[GPTService, Depends(create_gpt_service)]