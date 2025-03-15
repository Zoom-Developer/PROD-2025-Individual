from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile

from api import get_campaign, get_current_day
from utils.image import image_id2url
from .start import send_start_menu


async def send_campaign_menu(bot: Bot, chat_id: int, state: FSMContext):
    data = await state.get_data()
    campaign = await get_campaign(data.get("advertiser_id"), data.get("campaign_id"))
    if not campaign:
        return await send_start_menu(bot, chat_id, state)
    now = await get_current_day()
    current_date = await get_current_day()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        *(
            [[InlineKeyboardButton(text="Редактирование рекламной кампании", callback_data="edit_campaign")]]
            if now <= campaign.end_date else []
        ),
        [InlineKeyboardButton(text="Статистика рекламной кампании", callback_data="stat_campaign")],
        [InlineKeyboardButton(text="🗑 Удалить рекламную кампанию", callback_data="delete_campaign")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advert_menu")]
    ])

    title_text = f"<b>{campaign.ad_title}</b>"
    if current_date > campaign.end_date:
        title_text += f" <code>[ЗАКОНЧИЛА РАБОТУ]</code>"
    elif current_date >= campaign.start_date:
        title_text += f" <code>[В РАБОТЕ]</code>"

    text = (f"{title_text}\n"
       f"<i>{campaign.ad_text}</i>\n\n"
       f"Лимит показов: <code>{campaign.impressions_limit}</code>\n"
       f"Стоимость 1 показа: <code>{campaign.cost_per_impression}</code>\n"
       f"Лимит переходов: <code>{campaign.clicks_limit}</code>\n"
       f"Стоимость 1 перехода: <code>{campaign.cost_per_click}</code>\n"
       f"Продолжительность: <code>{campaign.start_date} -> {campaign.end_date}</code>\n"
       f"Пол ЦА: <code>{campaign.targeting.gender or 'ALL'}</code>\n"
       f"Возраст ЦА: <code>{campaign.targeting.age_from or 'ANY'} -> {campaign.targeting.age_to or 'ANY'}</code>\n"
       f"Локация ЦА: <code>{campaign.targeting.location or 'ANY'}</code>\n")

    if campaign.ad_image_url:
        await bot.send_photo(chat_id, caption=text, photo=URLInputFile(image_id2url(campaign.ad_image_id)), reply_markup=kb)
    else:
        await bot.send_message(chat_id, text, reply_markup=kb)

async def send_campaign_edit_menu(bot: Bot, chat_id: int, state: FSMContext):
    data = await state.get_data()
    now = await get_current_day()
    campaign = await get_campaign(data.get("advertiser_id"), data.get("campaign_id"))
    if not campaign:
        return await send_start_menu(bot, chat_id, state)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text = "Название кампании", callback_data="ecamp_title"),
            InlineKeyboardButton(text = "Текст кампании", callback_data="ecamp_text")
        ],
        [
            InlineKeyboardButton(text = "Цена за 1 показ", callback_data="ecamp_impression_cost"),
            InlineKeyboardButton(text = "Цена за 1 переход", callback_data="ecamp_clicks_cost")
        ],
        [
            InlineKeyboardButton(text="Целевая аудитория", callback_data="ecamp_target_gender"),
            InlineKeyboardButton(text="Изображение кампании", callback_data="ecamp_image"),
        ],
        *(([
            InlineKeyboardButton(text="Дата начала", callback_data="ecamp_start_date"),
            InlineKeyboardButton(text="Дата окончания", callback_data="ecamp_end_date")
        ],
        [
            InlineKeyboardButton(text="Максимальное количество показов", callback_data="ecamp_impressions_limit"),
        ],
        [
            InlineKeyboardButton(text="Максимальное количество переходов", callback_data="ecamp_clicks_limit")
        ]) if now < campaign.start_date else ()),
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="campaign_menu"),
        ]
    ])

    await bot.send_message(chat_id, "<b>Что вы хотите изменить?</b>", reply_markup=kb)