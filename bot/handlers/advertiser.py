import io

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile

from api import gen_ad_text_ai, upload_file, create_campaign, BaseCampaign, get_current_day, bulk_advertiser
from api.models import CampaignTarget
from exc import APIError
from menus import send_advertiser_menu, send_campaign_menu, send_find_campaign_menu
from menus.stats import send_stat_menu
from shared import SKIP_KEYBOARD
from states import RegCampaignState, EditAdvertiserState
from utils.image import image_id2url
from utils.nums import is_float

router = Router()


@router.callback_query(F.data == "advert_menu")
async def to_adv_menu(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()

    await send_advertiser_menu(query.bot, query.message.chat.id, state)

@router.callback_query(F.data == "stat_advertiser")
async def show_stat(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()

    await send_stat_menu(query.bot, query.message.chat.id, state, False)

# ------------------
# EDIT ADVERTISER
# ------------------

@router.callback_query(F.data == "name_advertiser")
async def on_edit_name(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.set_state(EditAdvertiserState.name)

    await query.message.answer("Введите новое название рекламодателя")

@router.message(EditAdvertiserState.name)
async def edit_name(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'])
    await bulk_advertiser(data['advertiser_id'], msg.text)
    await msg.answer("✅ Имя изменено")

    await send_advertiser_menu(msg.bot, msg.chat.id, state)

# ------------------
# REG CAMPAIGNS
# ------------------

@router.callback_query(F.data == "reg_campaign")
async def on_reg_campaign(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.set_state(RegCampaignState.title)

    await query.bot.send_message(query.message.chat.id, "Шаг 1/13. Введите название вашей рекламной кампании")

@router.message(RegCampaignState.title)
async def on_title(msg: Message, state: FSMContext):
    await state.set_state(RegCampaignState.text)
    await state.update_data(title=msg.text)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text = "Сгенерировать", callback_data="gen_ai_text")
    ]])

    await msg.answer("Шаг 2/13. Возможно вы хотите сгенерировать текст вашей рекламной кампании при помощи ИИ "
                     "на основе вашего названия и названия вашей рекламной кампании?"
                     "\nЕсли нет, то введите текст сами", reply_markup=kb)

@router.callback_query(F.data == "gen_ai_text", RegCampaignState.text)
async def on_ai_gen(query: CallbackQuery, state: FSMContext):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data="accept_ai_text")],
        [InlineKeyboardButton(text="❌ Повторная генерация", callback_data="gen_ai_text")],
    ])

    text = await gen_ad_text_ai(await state.get_value("title"), await state.get_value("advertiser_id"))
    await query.answer()
    await query.message.delete()
    await state.update_data(text=text)

    await query.bot.send_message(
        query.message.chat.id,
        f"<b>Предложенный вариант от нейросети:</b>\n<i>{text}</i>\n\n"
        "Вы можете написать свой текст, повторить генерацию или выбрать этот вариант",
        reply_markup=kb
    )

async def send_image_msg(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(RegCampaignState.image)

    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text = "Пропустить", callback_data="skip")
    ]])
    await bot.send_message(
        chat_id,
        "Шаг 3/13. При желании, отправьте фотографию на заставку вашей кампании",
        reply_markup=kb
    )

@router.callback_query(F.data == "accept_ai_text", RegCampaignState.text)
async def on_accept_ai(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()

    await send_image_msg(query.bot, query.message.chat.id, state)

@router.message(RegCampaignState.text)
async def on_text(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    await send_image_msg(msg.bot, msg.chat.id, state)

async def send_impression_limit(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(RegCampaignState.impressions_limit)
    await bot.send_message(chat_id, "Шаг 4/13. Введите максимальное кол-во отображений рекламы")

@router.message((F.document != None) | (F.photo != None), RegCampaignState.image)
async def on_send_image(msg: Message, state: FSMContext):
    file = io.BytesIO()
    await msg.bot.download(msg.document or msg.photo[-1], file)

    file.seek(0)
    image_id, _ = await upload_file(file.read())
    if not image_id:
        return await msg.answer("⚠️ Отправленный файл не является валидным изображением!")

    await state.update_data(image_id=image_id)
    await send_impression_limit(msg.bot, msg.chat.id, state)

@router.callback_query(F.data == "skip", RegCampaignState.image)
async def on_send_image(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(image_id=None)
    await send_impression_limit(query.bot, query.message.chat.id, state)

@router.message(RegCampaignState.impressions_limit)
async def on_impression_limit(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    await state.update_data(impression_limit=int(msg.text))
    await state.set_state(RegCampaignState.impression_cost)
    await msg.answer("Шаг 5/13. Введите стоимость одного просмотра")

@router.message(RegCampaignState.impression_cost)
async def on_impression_cost(msg: Message, state: FSMContext):
    if not is_float(msg.text):
        return await msg.answer("⚠️ Введено невалидное число!")
    await state.update_data(impression_cost=float(msg.text))
    await state.set_state(RegCampaignState.clicks_limit)
    await msg.answer("Шан 6/13. Введите максимальное кол-во переходов")

@router.message(RegCampaignState.clicks_limit)
async def on_clicks_limit(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    if int(msg.text) > await state.get_value("impression_limit"):
        return await msg.answer("⚠️ Лимит переходов не может быть больше лимита показов!")
    await state.update_data(clicks_limit=int(msg.text))
    await state.set_state(RegCampaignState.clicks_cost)
    await msg.answer("Шаг 7/13. Введите стоимость одного перехода")

@router.message(RegCampaignState.clicks_cost)
async def on_clicks_cost(msg: Message, state: FSMContext):
    if not is_float(msg.text):
        return await msg.answer("⚠️ Введено невалидное число!")
    await state.update_data(clicks_cost=float(msg.text))
    await state.set_state(RegCampaignState.start_date)
    await msg.answer("Шаг 8/13. Введите дату начала рекламной кампании")

@router.message(RegCampaignState.start_date)
async def on_start_date(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    now = await get_current_day()
    if now > int(msg.text):
        return await msg.answer(f"⚠️ Дата начала кампании не может быть в прошлом (сейчас {now})!")
    await state.update_data(start_date=int(msg.text))
    await state.set_state(RegCampaignState.end_date)
    await msg.answer("Шаг 9/13. Введите дату конца рекламной кампании")

@router.message(RegCampaignState.end_date)
async def on_end_date(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    if await state.get_value("start_date") > int(msg.text):
        return await msg.answer("⚠️ Дата конца рекламной кампании не может быть меньше начала!")
    await state.update_data(end_date=int(msg.text))
    await state.set_state(RegCampaignState.target_gender)

    await msg.answer("Шаг 10/13. Введите пол целевой аудитории (male/female/all)", reply_markup=SKIP_KEYBOARD)

async def send_target_age_from(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(RegCampaignState.target_age_from)
    await bot.send_message(chat_id, "Шаг 11/13. Введите минимальный возраст целевой аудитории", reply_markup=SKIP_KEYBOARD)

@router.callback_query(F.data == "skip", RegCampaignState.target_gender)
async def on_target_gender_skip(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_gender=None)
    await send_target_age_from(query.bot, query.message.chat.id, state)

@router.message(RegCampaignState.target_gender)
async def on_target_gender(msg: Message, state: FSMContext):
    if msg.text.lower() not in ["male", "female", "all"]:
        return await msg.answer("⚠️ Введён неправильный пол (male/female/all)")
    await state.update_data(target_gender=msg.text.upper())
    await send_target_age_from(msg.bot, msg.chat.id, state)

async def send_target_age_to(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(RegCampaignState.target_age_to)
    await bot.send_message(chat_id, "Шаг 12/13. Введите максимальный возраст целевой аудитории", reply_markup=SKIP_KEYBOARD)

@router.callback_query(F.data == "skip", RegCampaignState.target_age_from)
async def on_target_age_from_skip(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_age_from=None)
    await send_target_age_to(query.bot, query.message.chat.id, state)

@router.message(RegCampaignState.target_age_from)
async def on_target_age_from(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    await state.update_data(target_age_from=int(msg.text))
    await send_target_age_to(msg.bot, msg.chat.id, state)

async def send_target_location(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(RegCampaignState.target_location)
    await bot.send_message(chat_id, "Шаг 13/13. Введите локацию целевой аудитории", reply_markup=SKIP_KEYBOARD)

@router.callback_query(F.data == "skip", RegCampaignState.target_age_to)
async def on_target_age_to_skip(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_age_to=None)
    await send_target_location(query.bot, query.message.chat.id, state)

@router.message(RegCampaignState.target_age_to)
async def on_target_age_to(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    if int(msg.text) < (await state.get_value("target_age_from") or 0):
        return await msg.answer("⚠️ Максимальный возраст не может быть меньше минимального!")
    await state.update_data(target_age_to=int(msg.text))
    await send_target_location(msg.bot, msg.chat.id, state)

async def send_confirm(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(RegCampaignState.confirm)
    data = await state.get_data()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Продолжить", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Повторить заполнение", callback_data="reg_campaign")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="advert_menu")]
    ])
    text = ("Отлично, вы заполнили все поля.\n\n"
            f"<b>{data['title']}</b>\n"
            f"<i>{data['text']}</i>\n\n"
            f"Лимит показов: <code>{data['impression_limit']}</code>\n"
            f"Стоимость 1 показа: <code>{data['impression_cost']}</code>\n"
            f"Лимит переходов: <code>{data['clicks_limit']}</code>\n"
            f"Стоимость 1 перехода: <code>{data['clicks_cost']}</code>\n"
            f"Продолжительность: <code>{data['start_date']} -> {data['end_date']}</code>\n"
            f"Пол ЦА: <code>{data['target_gender'] or 'ALL'}</code>\n"
            f"Возраст ЦА: <code>{data['target_age_from'] or 'ANY'} -> {data['target_age_to'] or 'ANY'}</code>\n"
            f"Локация ЦА: <code>{data['target_location'] or 'ANY'}</code>\n")

    if data['image_id']:
        await bot.send_photo(chat_id, URLInputFile(image_id2url(data['image_id'])), caption=text, reply_markup=kb)
    else:
        await bot.send_message(chat_id, text, reply_markup=kb)

@router.callback_query(F.data == "skip", RegCampaignState.target_location)
async def on_target_age_to_skip(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_location=None)
    await send_confirm(query.bot, query.message.chat.id, state)

@router.message(RegCampaignState.target_location)
async def on_target_age_to(msg: Message, state: FSMContext):
    await state.update_data(target_location=msg.text)
    await send_confirm(msg.bot, msg.chat.id, state)

@router.callback_query(F.data == "confirm", RegCampaignState.confirm)
async def on_confirm(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        campaign = await create_campaign(
            data['advertiser_id'],
            BaseCampaign(
                impressions_limit=data['impression_limit'],
                cost_per_impression=data['impression_cost'],
                clicks_limit=data['clicks_limit'],
                cost_per_click=data['clicks_cost'],
                ad_title=data['title'],
                ad_text=data['text'],
                ad_image_id=data['image_id'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                targeting=CampaignTarget(
                    gender=data['target_gender'],
                    age_from=data['target_age_from'],
                    age_to=data['target_age_to'],
                    location=data['target_location']
                )
            ),
        )
    except APIError as e:
        if e.status_code == 422:
            await query.bot.send_message(query.message.chat.id, "⚠️ Дата старта кампании должна быть как минимум текущим днём!")
        elif e.status_code == 403:
            await query.bot.send_message(query.message.chat.id, "⚠️ Ваш рекламный текст или название не соответствует нормам этики!")
        else:
            await query.bot.send_message(query.message.chat.id, "⚠️ Произошла неизвестная ошибка...")
        await state.clear()
        await state.update_data(advertiser_id=data['advertiser_id'])
        return await send_advertiser_menu(query.bot, query.message.chat.id, state)
    finally:
        await query.answer()
        await query.message.delete()

    await state.clear()
    await state.update_data(campaign_id=campaign.campaign_id, advertiser_id=campaign.advertiser_id)

    await send_campaign_menu(query.bot, query.message.chat.id, state)

# ------------------
# FIND CAMPAIGNS
# ------------------

@router.callback_query(F.data == "find_campaign")
async def find_campaign(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()

    await send_find_campaign_menu(query.bot, query.message.chat.id, state, 1)

@router.callback_query(F.data.startswith("fcamp_"))
async def find_campaign_page(query: CallbackQuery, state: FSMContext):
    await send_find_campaign_menu(query.bot, query.message.chat.id, state, int(query.data.replace("fcamp_", "")))

    await query.answer()
    await query.message.delete()

@router.callback_query(F.data.startswith("camp_"))
async def select_campaign(query: CallbackQuery, state: FSMContext):
    await state.update_data(campaign_id=query.data.replace("camp_", ""))
    await send_campaign_menu(query.bot, query.message.chat.id, state)

    await query.answer()
    await query.message.delete()
