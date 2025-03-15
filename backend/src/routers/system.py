from fastapi import APIRouter
from sqlalchemy import delete

from src.core.db import ping_db, SessionDep
from src.core.exc import ValidationError, HTTPErrorModel
from src.core.utils import get_current_day, update_day, update_enabled_moderation, get_enabled_moderation
from src.models import ClientViewCampaign
from src.schemes import DateModel, SecurityModeration, UpdateMLScoreRequest, UpdateMLScoreResponse
from src.service.advertiser import AdvertiserServiceDep

router = APIRouter(tags=["System"])

@router.post(
    "/time/advance"
)
async def set_day(data: DateModel) -> DateModel:
    """
    Установка текущего дня<br>
    Возвращает `422` при попытке поставить дату в прошлом
    """
    now = await get_current_day()
    if data.current_date < now:
        raise ValidationError("can not set date in the past")
    await update_day(data.current_date)
    return DateModel(current_date=data.current_date)

@router.get("/time")
async def get_day() -> DateModel:
    """
    Получение текущего дня
    """
    return DateModel(current_date=await get_current_day())

@router.patch("/security/moderation")
async def set_moderation(data: SecurityModeration) -> SecurityModeration:
    """
    Изменение текущей политики модерации, влияющий на модерацию контента рекламных кампаний
    """
    await update_enabled_moderation(data.is_enabled)
    return SecurityModeration(is_enabled=data.is_enabled)

@router.get("/security/moderation")
async def get_moderation() -> SecurityModeration:
    """
    Получение текущей политики модерации, влияющий на модерацию контента рекламных кампаний
    """
    return SecurityModeration(is_enabled=await get_enabled_moderation())

@router.get("/system/ping", include_in_schema=False)
async def ping(session: SessionDep):
    """
    Используется для процедуры healthcheck
    """
    await ping_db(session)
    return True

@router.post(
    "/ml-scores",
    tags=["Advertisers"],
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Клиент или рекламодатель не найден"
        }
    }
)
async def update_mlscore(data: UpdateMLScoreRequest, service: AdvertiserServiceDep) -> UpdateMLScoreResponse:
    """
    Обновление ML Score<br>
    Возвращает `404` в случае если клиент или рекламодатель не найден
    """
    await service.update_score(data.client_id, data.advertiser_id, data.score)
    return UpdateMLScoreResponse()

@router.delete("/views", include_in_schema=False, status_code=204)
async def delete_views(session: SessionDep):
    """
    Необходима для автоматической очистки просмотров в рамках тестирования алгоритма
    """
    await session.exec(delete(ClientViewCampaign))