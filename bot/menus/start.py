from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from api import find_advertisers
from shared import BACK_KEYBOARD
from utils.search_keyboard import create_search_keyboard


async def send_start_menu(bot: Bot, chat_id: int, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "👤 Регистрация рекламодателя", callback_data="reg_adv")],
        [InlineKeyboardButton(text = "👤 Выбор рекламодателя", callback_data="find_advertisers")],
        [InlineKeyboardButton(text = "👨‍💻 Регистрация клиента", callback_data="reg_client")],
        [InlineKeyboardButton(text = "👀 Просмотр рекламы", callback_data="watch_ads")],
        [InlineKeyboardButton(text = "🌙 Смена текущего дня", callback_data="set_day")],
    ])

    await bot.send_message(
        chat_id,
        "Привет! Что ты хочешь сделать?",
        reply_markup=kb
    )

async def send_find_advertiser_menu(bot: Bot, chat_id: int, page: int):
    find = await find_advertisers(page, 5)

    if find.total_pages == 0:
        return await bot.send_message(
            chat_id,
            "<b>Список рекламодателей пуст</b>",
            reply_markup=BACK_KEYBOARD
        )

    kb = create_search_keyboard(
        find.current_page,
        find.total_pages,
        "adv",
        find.advertisers,
        "name",
        "advertiser_id",
        "to_start"
    )

    await bot.send_message(
        chat_id,
        "<b>Список всех рекламодателей</b>",
        reply_markup=kb
    )