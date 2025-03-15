import asyncio

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from redis.asyncio import Redis

from config import config
from handlers import start_router, advertiser_router, campaign_router, stats_router, other_router, ad_router


async def main():
    dp = Dispatcher(
        storage=RedisStorage(
            redis=Redis(
                host=config.redis_host,
                port=config.redis_port
            )
        )
    )

    dp.include_routers(
        start_router,
        advertiser_router,
        campaign_router,
        stats_router,
        other_router,
        ad_router
    )

    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота")
    ])

    print("Start polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())