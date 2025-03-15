from typing import Literal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


BACK_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text = "◀️ Назад", callback_data="to_start")
]])

SKIP_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Пропустить", callback_data="skip")
]])

GENDER = Literal["MALE", "FEMALE"]
FULL_GENDER = Literal["MALE", "FEMALE", "ALL"]