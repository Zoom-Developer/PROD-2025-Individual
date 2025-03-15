from aiogram.fsm.state import StatesGroup, State


class RegAdvertiserState(StatesGroup):
    name = State()

class ChoiceAdvertiserState(StatesGroup):
    id = State()

class EditAdvertiserState(StatesGroup):
    name = State()

class RegCampaignState(StatesGroup):
    title = State()
    ai_text = State()
    text = State()
    image = State()
    impressions_limit = State()
    impression_cost = State()
    clicks_limit = State()
    clicks_cost = State()
    start_date = State()
    end_date = State()
    target_gender = State()
    target_age_from = State()
    target_age_to = State()
    target_location = State()
    confirm = State()

class EditCampaignState(StatesGroup):
    title = State()
    text = State()
    impressions_limit = State()
    clicks_limit = State()
    impression_cost = State()
    clicks_cost = State()
    start_date = State()
    end_date = State()
    target_gender = State()
    target_age_from = State()
    target_age_to = State()
    target_location = State()
    image = State()

class WatchAdState(StatesGroup):
    watch = State()

class SetTimeState(StatesGroup):
    time = State()

class RegClientState(StatesGroup):
    login = State()
    age = State()
    location = State()
    gender = State()