import io

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from api import delete_campaign, edit_campaign, upload_file, get_campaign, gen_ad_text_ai
from api.models import CampaignTarget
from exc import APIError
from menus import send_advertiser_menu, send_campaign_edit_menu, send_campaign_menu, send_start_menu
from menus.stats import send_stat_menu
from shared import SKIP_KEYBOARD
from states import EditCampaignState
from utils.nums import is_float

router = Router()

@router.callback_query(F.data == "delete_campaign")
async def del_camp(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("campaign_id"):
        return await send_start_menu(query.bot, query.message.chat.id, state)
    await delete_campaign(data['advertiser_id'], data['campaign_id'])
    await query.answer()
    await query.message.delete()

    await send_advertiser_menu(query.bot, query.message.chat.id, state)

@router.callback_query(F.data == "edit_campaign")
async def edit_camp(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()

    await send_campaign_edit_menu(query.bot, query.message.chat.id, state)

@router.callback_query(F.data == "campaign_menu")
async def camp_menu(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()

    await send_campaign_menu(query.bot, query.message.chat.id, state)

@router.callback_query(F.data == "stat_campaign")
async def show_stat(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()

    await send_stat_menu(query.bot, query.message.chat.id, state, True)

# ------------------
# EDIT CAMPAIGN
# ------------------

@router.callback_query(F.data.startswith("ecamp_"))
async def on_edit_campaign(query: CallbackQuery, state: FSMContext):
    edit_type = query.data.replace("ecamp_", "")
    await state.set_state(getattr(EditCampaignState, edit_type))
    await query.answer()
    await query.message.delete()

    data = await state.get_data()
    campaign = await get_campaign(data['advertiser_id'], data['campaign_id'])

    match edit_type:
        case "title":
            await query.bot.send_message(query.message.chat.id, "Введите новое название кампании")
        case "text":
            await query.bot.send_message(
                query.message.chat.id,
                "Введите новый текст кампании",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text = "Сгенерировать с помощью ИИ", callback_data="ai_text")
                ]])
            )
        case "impression_cost":
            await query.bot.send_message(query.message.chat.id, "Введите новую цену за показ")
        case "clicks_cost":
            await query.bot.send_message(query.message.chat.id, "Введите новую цену за переход")
        case "impressions_limit":
            await query.bot.send_message(query.message.chat.id, "Введите новое максимальное кол-во показов")
        case "clicks_limit":
            await query.bot.send_message(query.message.chat.id, "Введите новое максимальное кол-во переходов")
        case "start_date":
            await query.bot.send_message(query.message.chat.id, "Введите новую дату начала рекламной кампании")
        case "end_date":
            await query.bot.send_message(query.message.chat.id, "Введите новую дату конца рекламной кампании")
        case "target_gender":
            await query.bot.send_message(
                query.message.chat.id,
                "Введите новый пол ЦА (male/female/all)",
                reply_markup=SKIP_KEYBOARD
            )
        case "image":
            await query.bot.send_message(
                query.message.chat.id,
                "Отправьте новое изображение",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text = "🗑 Удалить существующее изображение", callback_data="del_img")
                ]]) if campaign.ad_image_id else None
            )

@router.message(EditCampaignState.title)
async def edit_campaign_title(msg: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await edit_campaign(data['advertiser_id'], data['campaign_id'], ad_title = msg.text)
    except APIError as e:
        if e.status_code == 403:
            return await msg.answer("⚠️ Ваше рекламное название не соответствует нормам этики!")
    await state.clear()
    await state.update_data(advertiser_id = data['advertiser_id'], campaign_id = data['campaign_id'])
    await msg.answer("✅ Название изменено")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.callback_query(F.data == "ai_text", EditCampaignState.text)
async def gen_ai_text(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    campaign = await get_campaign(data['advertiser_id'], data['campaign_id'])

    text = await gen_ad_text_ai(campaign.ad_title, data['advertiser_id'])
    await query.answer()
    await query.message.delete()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data="accept_ai_text")],
        [InlineKeyboardButton(text="❌ Повторная генерация", callback_data="ai_text")],
    ])

    await state.update_data(text = text)
    await query.bot.send_message(
        query.message.chat.id,
        f"<b>Предложенный вариант от нейросети:</b>\n<i>{text}</i>\n\n"
        "Вы можете написать свой текст, повторить генерацию или выбрать этот вариант",
        reply_markup=kb
    )

@router.callback_query(F.data == "accept_ai_text", EditCampaignState.text)
async def accept_ai_text(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        await edit_campaign(data['advertiser_id'], data['campaign_id'], ad_text=data['text'])
    except APIError as e:
        if e.status_code == 403:
            return await query.bot.send_message(query.message.chat.id, "⚠️ Ваш рекламный текст не соответствует нормам этики!")
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await query.answer()
    await query.message.delete()
    await query.bot.send_message(query.message.chat.id, "✅ Текст изменён")
    await send_campaign_edit_menu(query.bot, query.message.chat.id, state)

@router.message(EditCampaignState.text)
async def edit_campaign_text(msg: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await edit_campaign(data['advertiser_id'], data['campaign_id'], ad_text = msg.text)
    except APIError as e:
        if e.status_code == 403:
            return await msg.answer("⚠️ Ваш рекламный текст не соответствует нормам этики!")
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await msg.answer("✅ Текст изменён")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.message(EditCampaignState.impression_cost)
async def edit_campaign_imp_cost(msg: Message, state: FSMContext):
    if not is_float(msg.text):
        return await msg.answer("⚠️ Введено невалидное число!")
    data = await state.get_data()
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await edit_campaign(data['advertiser_id'], data['campaign_id'], cost_per_impression = float(msg.text))
    await msg.answer("✅ Стоимость показа изменена")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.message(EditCampaignState.clicks_cost)
async def edit_campaign_clicks_cost(msg: Message, state: FSMContext):
    if not is_float(msg.text):
        return await msg.answer("⚠️ Введено невалидное число!")
    data = await state.get_data()
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await edit_campaign(data['advertiser_id'], data['campaign_id'], cost_per_click = float(msg.text))
    await msg.answer("✅ Стоимость перехода изменена")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.message(EditCampaignState.impressions_limit)
async def edit_campaign_impressions_limit(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    data = await state.get_data()
    try:
        await edit_campaign(data['advertiser_id'], data['campaign_id'], impressions_limit = int(msg.text))
    except APIError as e:
        if e.status_code == 422:
            return await msg.answer("⚠️ Лимит переходов не может быть больше лимита показов!")
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await msg.answer("✅ Лимит показов изменён")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.message(EditCampaignState.clicks_limit)
async def edit_campaign_clicks_limit(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    data = await state.get_data()
    try:
        await edit_campaign(data['advertiser_id'], data['campaign_id'], clicks_limit = int(msg.text))
    except APIError as e:
        if e.status_code == 422:
            return await msg.answer("⚠️ Лимит переходов не может быть больше лимита показов!")
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await msg.answer("✅ Лимит переходов изменён")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.message(EditCampaignState.start_date)
async def edit_campaign_start_date(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    data = await state.get_data()
    try:
        await edit_campaign(data['advertiser_id'], data['campaign_id'], start_date = int(msg.text))
    except APIError as e:
        if e.status_code == 422:
            return await msg.answer("⚠️ Дата начала рекламной кампании не может быть в прошлом!")
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await msg.answer("✅ Дата начала кампании изменена")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.message(EditCampaignState.end_date)
async def edit_campaign_start_date(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    data = await state.get_data()
    try:
        await edit_campaign(data['advertiser_id'], data['campaign_id'], end_date = int(msg.text))
    except APIError as e:
        if e.status_code == 422:
            return await msg.answer("⚠️ Дата конца рекламной кампании не может быть больше начала!")
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await msg.answer("✅ Дата конца кампании изменена")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

@router.callback_query(F.data == "del_img", EditCampaignState.image)
async def delete_image(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])

    await edit_campaign(data['advertiser_id'], data['campaign_id'], ad_image_id=None)
    await query.answer()
    await query.message.delete()
    await query.message.answer("✅ Изображено удалено")
    await send_campaign_edit_menu(query.bot, query.message.chat.id, state)

@router.message((F.document != None) | (F.photo != None), EditCampaignState.image)
async def edit_image(msg: Message, state: FSMContext):
    file = io.BytesIO()
    await msg.bot.download(msg.document or msg.photo[-1], file)

    file.seek(0)
    image_id, image_url = await upload_file(file.read())
    if not image_id:
        return await msg.answer("⚠️ Отправленный файл не является валидным изображением!")

    data = await state.get_data()
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await edit_campaign(data['advertiser_id'], data['campaign_id'], ad_image_id = image_id)
    await msg.answer("✅ Изображение изменено")
    await send_campaign_edit_menu(msg.bot, msg.chat.id, state)

async def send_age_from(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(EditCampaignState.target_age_from)
    await bot.send_message(chat_id, "Введите новый минимальный возраст ЦУ", reply_markup=SKIP_KEYBOARD)

@router.callback_query(F.data == "skip", EditCampaignState.target_gender)
async def skip_campaign_gender(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_gender = None)
    await send_age_from(query.bot, query.message.chat.id, state)

@router.message(EditCampaignState.target_gender)
async def edit_campaign_gender(msg: Message, state: FSMContext):
    if msg.text.lower() not in ["male", "female", "all"]:
        return await msg.answer("⚠️ Введён неправильный пол (male/female/all)!")
    await state.update_data(target_gender = msg.text.upper())
    await send_age_from(msg.bot, msg.chat.id, state)

async def send_campaign_age_to(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(EditCampaignState.target_age_to)
    await bot.send_message(chat_id, "Введите новый максимальный возраст ЦУ", reply_markup=SKIP_KEYBOARD)

@router.callback_query(F.data == "skip", EditCampaignState.target_age_from)
async def skip_campaign_age_from(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_age_from=None)
    await send_campaign_age_to(query.bot, query.message.chat.id, state)

@router.message(EditCampaignState.target_age_from)
async def edit_campaign_age_from(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    await state.update_data(target_age_from = int(msg.text))
    await send_campaign_age_to(msg.bot, msg.chat.id, state)

async def send_campaign_location(bot: Bot, chat_id: int, state: FSMContext):
    await state.set_state(EditCampaignState.target_location)
    await bot.send_message(chat_id, "Введите новую локацию ЦУ", reply_markup=SKIP_KEYBOARD)

@router.callback_query(F.data == "skip", EditCampaignState.target_age_to)
async def skip_campaign_age_to(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_age_to=None)
    await send_campaign_location(query.bot, query.message.chat.id, state)

@router.message(EditCampaignState.target_age_to)
async def edit_campaign_age_to(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        return await msg.answer("⚠️ Введено невалидное число!")
    if int(msg.text) < (await state.get_value("target_age_from") or 0):
        return await msg.answer("⚠️ Максимальный возраст не может быть меньше минимального!")
    await state.update_data(target_age_to = int(msg.text))
    await send_campaign_location(msg.bot, msg.chat.id, state)

async def edit_campaign_target(bot: Bot, chat_id: int, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await state.update_data(advertiser_id=data['advertiser_id'], campaign_id=data['campaign_id'])
    await edit_campaign(data['advertiser_id'], data['campaign_id'], targeting=CampaignTarget(
        age_from=data['target_age_from'],
        age_to=data['target_age_to'],
        gender=data['target_gender'],
        location=data['target_location']
    ).model_dump())
    await bot.send_message(chat_id, "✅ Целевая аудитория изменена")
    await send_campaign_edit_menu(bot, chat_id, state)

@router.callback_query(F.data == "skip", EditCampaignState.target_location)
async def skip_campaign_location(query: CallbackQuery, state: FSMContext):
    await query.answer()
    await query.message.delete()
    await state.update_data(target_location=None)
    await edit_campaign_target(query.bot, query.message.chat.id, state)

@router.message(EditCampaignState.target_location)
async def edit_campaign_location(msg: Message, state: FSMContext):
    await state.update_data(target_location = msg.text)
    await edit_campaign_target(msg.bot, msg.chat.id, state)