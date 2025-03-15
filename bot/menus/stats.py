from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from menus import send_start_menu


async def send_stat_menu(bot: Bot, chat_id: int, state: FSMContext, is_campaign: bool):

    data = await state.update_data(is_campaign=is_campaign)
    if not data.get("advertiser_id"):
        return await send_start_menu(bot, chat_id, state)
    if is_campaign and data.get("campaign_id") is None:
        return await send_start_menu(bot, chat_id, state)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Агрегированная", callback_data="stat_agr"),
            InlineKeyboardButton(text="Дневная", callback_data="stat_daily")
        ],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="campaign_menu" if is_campaign else "advert_menu")]
    ])

    await bot.send_message(chat_id, "<b>Какой тип статистики вы хотите увидеть?</b>", reply_markup=kb)