from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from api import click_ad
from menus.ad import send_ad_menu
from states import WatchAdState


router = Router()

@router.callback_query(F.data == "watch_ads")
async def on_watch_ads(query: CallbackQuery, state: FSMContext):
    await state.set_state(WatchAdState.watch)
    await send_ad_menu(query.bot, query.message.chat.id, state)
    await query.message.delete()

@router.callback_query(F.data.startswith("click_"), WatchAdState.watch)
async def on_click_ad(query: CallbackQuery, state: FSMContext):
    await click_ad(query.data.replace("click_", ""), await state.get_value("client_id"))
    await send_ad_menu(query.bot, query.message.chat.id, state)
    await query.message.delete()

@router.callback_query(F.data == "next", WatchAdState.watch)
async def on_next_ad(query: CallbackQuery, state: FSMContext):
    await send_ad_menu(query.bot, query.message.chat.id, state)
    await query.message.delete()
