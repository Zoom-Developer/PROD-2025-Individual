from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile

from api import get_random_client, get_advert
from shared import BACK_KEYBOARD
from utils.image import image_id2url


async def send_ad_menu(bot: Bot, chat_id: int, state: FSMContext):
    client = await get_random_client()

    if not client:
        return await bot.send_message(chat_id, "⚠️ Нет ни одного клиента!", reply_markup=BACK_KEYBOARD)
    ad = await get_advert(client.client_id)
    if not ad:
        return await bot.send_message(
            chat_id,
            "⚠️ Объявления кончились!",
          reply_markup=InlineKeyboardMarkup(inline_keyboard=[
              [InlineKeyboardButton(text="▶️ Дальше", callback_data=f"next")], # Объявления могут быть у другого клиента
              [InlineKeyboardButton(text="❌ Выйти", callback_data="to_start")]
          ])
        )

    await state.update_data(client_id=client.client_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "👊 Кликнуть", callback_data=f"click_{ad.ad_id}")],
        [InlineKeyboardButton(text = "▶️ Дальше", callback_data=f"next")],
        [InlineKeyboardButton(text = "❌ Выйти", callback_data="to_start")]
    ])

    text = f"<b>{ad.ad_title}</b>\n<i>{ad.ad_text}</i>"
    if ad.ad_image_id:
        await bot.send_photo(chat_id, URLInputFile(image_id2url(ad.ad_image_id)), caption=text, reply_markup=kb)
    else:
        await bot.send_message(chat_id, text, reply_markup=kb)