from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from api import get_stat_campaign, get_stat_advertiser, get_stat_campaign_daily, get_stat_advertiser_daily
from menus import send_start_menu

router = Router()

@router.callback_query(F.data == "stat_agr")
async def on_stat(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get("is_campaign") is None:
        await query.message.delete()
        return await send_start_menu(query.bot, query.message.chat.id, state)
    if data['is_campaign']:
        stat = await get_stat_campaign(data['campaign_id'])
    else:
        stat = await get_stat_advertiser(data['advertiser_id'])

    await query.message.delete()
    await query.answer()

    await query.bot.send_message(
        query.message.chat.id,
        "<b>Агрегированная статистика</b>\n\n"
        f"Количество показов: <b>{stat.impressions_count}</b>\n"
        f"Количество переходов: <b>{stat.clicks_count}</b>\n"
        f"Конверсия: <b>{stat.conversion}%</b>\n\n"
        f"Потрачено на показы: {f'{stat.spent_impressions:,}'.replace(',', ' ')}\n"
        f"Потрачено на переходы: {f'{stat.spent_clicks:,}'.replace(',', ' ')}\n"
        f"Общие траты: {f'{stat.spent_total:,}'.replace(',', ' ')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="◀️ Назад", callback_data="stat_campaign" if data['is_campaign'] else "stat_advertiser")
        ]])
    )

@router.callback_query(F.data.startswith("stat_daily"))
async def on_stat_daily(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get("is_campaign") is None:
        await query.message.delete()
        return await send_start_menu(query.bot, query.message.chat.id, state)
    if data['is_campaign']:
        stat = await get_stat_campaign_daily(data['campaign_id'])
    else:
        stat = await get_stat_advertiser_daily(data['advertiser_id'])

    await query.message.delete()
    await query.answer()

    if not stat:
        return await query.bot.send_message(
            query.message.chat.id,
            "<b>Статистика отсутствует</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="◀️ Назад",
                                     callback_data="stat_campaign" if data['is_campaign'] else "stat_advertiser")
            ]])
        )

    if "stat_daily_" in query.data:
        page = int(query.data.split("_")[-1])
    else:
        page = 0

    await query.bot.send_message(
        query.message.chat.id,
        f"<b>Статистика за {stat[page].day} день</b>\n\n"
        f"Количество показов: <b>{stat[page].impressions_count}</b>\n"
        f"Количество переходов: <b>{stat[page].clicks_count}</b>\n"
        f"Конверсия: <b>{stat[page].conversion}%</b>\n\n"
        f"Потрачено на показы: {f'{stat[page].spent_impressions:,}'.replace(',', ' ')}\n"
        f"Потрачено на переходы: {f'{stat[page].spent_clicks:,}'.replace(',', ' ')}\n"
        f"Общие траты: {f'{stat[page].spent_total:,}'.replace(',', ' ')}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                *([InlineKeyboardButton(text="<", callback_data=f"stat_daily_{page - 1}")] if page > 0 else []),
                *([InlineKeyboardButton(text=">", callback_data=f"stat_daily_{page + 1}")] if page != len(stat) - 1 else [])
            ],
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="stat_campaign" if data['is_campaign'] else "stat_advertiser")
            ]
        ])
    )