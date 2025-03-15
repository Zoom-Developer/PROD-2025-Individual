import uuid

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from api import bulk_advertiser, register_client, ClientDTO, set_day, get_current_day
from exc import APIError
from menus import send_start_menu, send_advertiser_menu, send_find_advertiser_menu
from shared import BACK_KEYBOARD
from states import RegAdvertiserState, RegClientState, SetTimeState


router = Router()


@router.message(CommandStart())
async def on_start(msg: Message, state: FSMContext):
    await send_start_menu(msg.bot, msg.chat.id, state)

@router.callback_query(F.data == "to_start")
async def on_back_start(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await send_start_menu(query.bot, query.message.chat.id, state)

# ------------------
# SET TIME
# ------------------

@router.callback_query(F.data == "set_day")
async def on_back_start(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.answer()
    await state.set_state(SetTimeState.time)
    now = await get_current_day()
    await query.bot.send_message(
        query.message.chat.id,
        f"Отправьте новую дату (сегодня {now})",
        reply_markup=BACK_KEYBOARD
    )

@router.message(SetTimeState.time)
async def on_time(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено наверное число!")
    try:
        await set_day(int(msg.text))
    except APIError as e:
        if e.status_code == 422:
            return await msg.answer("⚠️ Новая дата должна быть больше и равна текущей!")
    await send_start_menu(msg.bot, msg.chat.id, state)

# ------------------
# REG ADVERTISER
# ------------------

@router.callback_query(F.data == "reg_adv")
async def reg_advertiser(query: CallbackQuery, state: FSMContext):
    await state.set_state(RegAdvertiserState.name)
    await query.message.delete()
    await query.answer()

    await query.bot.send_message(query.message.chat.id, "Отлично! Введите имя рекламодателя", reply_markup=BACK_KEYBOARD)

@router.message(RegAdvertiserState.name)
async def reg_adv(msg: Message, state: FSMContext):
    await state.clear()
    advertiser = await bulk_advertiser(str(uuid.uuid4()), msg.text)
    await state.update_data(advertiser_id=advertiser.advertiser_id)

    await send_advertiser_menu(msg.bot, msg.chat.id, state)

# ------------------
# CHOICE ADVERTISER
# ------------------

# @router.callback_query(F.data == "choice_adv")
# async def choice_adv(query: CallbackQuery, state: FSMContext):
#     await state.set_state(ChoiceAdvertiserState.id)
#     await query.message.delete()
#     await query.answer()
#
#     await query.bot.send_message(query.message.chat.id, "Отлично! Введите ID рекламодателя", reply_markup=BACK_KEYBOARD)
#
# @router.message(ChoiceAdvertiserState.id)
# async def choiced_adv(msg: Message, state: FSMContext):
#     advertiser = await get_advertiser(msg.text)
#     if not advertiser:
#         return await msg.answer("⚠️ Рекламодатель не найден, попробуйте снова", reply_markup=BACK_KEYBOARD)
#     await state.clear()
#     await state.update_data(advertiser_id=advertiser.advertiser_id)
#
#     await send_advertiser_menu(msg.bot, msg.chat.id, state)

# ------------------
# REG CLIENT
# ------------------

@router.callback_query(F.data == "reg_client")
async def on_reg_client(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.set_state(RegClientState.login)
    await query.bot.send_message(query.message.chat.id, "Шаг 1/4. Введите логин клиента")

@router.message(RegClientState.login)
async def on_login(msg: Message, state: FSMContext):
    await state.set_state(RegClientState.age)
    await state.update_data(login=msg.text)
    await msg.answer("Шаг 2/4. Введите возраст клиента")

@router.message(RegClientState.age)
async def on_age(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    await state.set_state(RegClientState.location)
    await state.update_data(age=int(msg.text))
    await msg.answer("Шаг 3/4. Введите локацию клиента")

@router.message(RegClientState.location)
async def on_login(msg: Message, state: FSMContext):
    await state.set_state(RegClientState.gender)
    await state.update_data(location=msg.text)
    await msg.answer("Шаг 4/4. Введите пол клиента (male/female)")

@router.message(RegClientState.gender)
async def on_gender(msg: Message, state: FSMContext):
    if msg.text.lower() not in ["male", "female"]:
        return await msg.answer("⚠️ Введён неверный пол (male/female)!")
    data = await state.update_data(gender=msg.text.upper())
    client = await register_client(ClientDTO(**data, client_id=str(uuid.uuid4())))
    await msg.answer(f"✅ Клиент зарегистрирован под ID {client.client_id}")
    await send_start_menu(msg.bot, msg.chat.id, state)

# ------------------
# FIND ADVERTISERS
# ------------------

@router.callback_query(F.data == "find_advertisers")
async def find_advertiser(query: CallbackQuery):
    await query.answer()
    await query.message.delete()

    await send_find_advertiser_menu(query.bot, query.message.chat.id, 1)

@router.callback_query(F.data.startswith("fadv_"))
async def find_advertiser_page(query: CallbackQuery):
    await send_find_advertiser_menu(query.bot, query.message.chat.id, int(query.data.replace("fadv_", "")))

    await query.answer()
    await query.message.delete()

@router.callback_query(F.data.startswith("adv_"))
async def select_advertiser(query: CallbackQuery, state: FSMContext):
    await state.update_data(advertiser_id=query.data.replace("adv_", ""))
    await send_advertiser_menu(query.bot, query.message.chat.id, state)

    await query.answer()
    await query.message.delete()
