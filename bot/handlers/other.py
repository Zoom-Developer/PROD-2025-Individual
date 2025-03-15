from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "null")
async def on_null(query: CallbackQuery):
    await query.answer()