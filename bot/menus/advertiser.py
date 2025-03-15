from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from api import get_advertiser, find_campaigns
from utils.search_keyboard import create_search_keyboard
from .start import send_start_menu


async def send_advertiser_menu(bot: Bot, chat_id: int, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await state.update_data(advertiser_id=data.get("advertiser_id"))
    advertiser = await get_advertiser(data.get("advertiser_id"))
    if not advertiser:
        return await send_start_menu(bot, chat_id, state)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Регистрация рекламной кампании", callback_data="reg_campaign")],
        [InlineKeyboardButton(text="Изменить название", callback_data="name_advertiser")],
        [InlineKeyboardButton(text="Рекламные кампании", callback_data="find_campaign")],
        [InlineKeyboardButton(text="Статистика рекламодателя", callback_data="stat_advertiser")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="to_start")]
    ])

    await bot.send_message(
        chat_id,
        f"Добро пожаловать, {advertiser.name}, что вы желаете сделать?",
        reply_markup=kb
    )

async def send_find_campaign_menu(bot: Bot, chat_id: int, state: FSMContext, page: int):
    data = await state.get_data()
    if not data.get("advertiser_id"):
        return await send_start_menu(bot, chat_id, state)
    find = await find_campaigns(data['advertiser_id'], page, 5)

    if find.total_pages == 0:
        return await bot.send_message(
            chat_id,
            "<b>Ваш список кампаний пуст</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text = "◀️ Назад", callback_data="advert_menu")
            ]])
        )

    kb = create_search_keyboard(
        find.current_page,
        find.total_pages,
        "camp",
        find.campaigns,
        "ad_title",
        "campaign_id",
        "advert_menu"
    )

    await bot.send_message(
        chat_id,
        "<b>Список всех ваших рекламных кампаний</b>",
        reply_markup=kb
    )