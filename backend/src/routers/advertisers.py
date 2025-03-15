import math

from fastapi import APIRouter, Depends, Query

from src.core.exc import HTTPErrorModel
from src.core.utils import remove_duplicated_ids
from src.models import Advertiser
from src.schemes import AdvertiserDTO, FindRequest, GetAdvertisersResponse
from src.service.advertiser import get_advertiser, AdvertiserServiceDep


router = APIRouter(prefix="/advertisers", tags=["Advertisers"])


@router.get(
    "/{advertiser_id}",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламодатель не найден"
        }
    }
)
async def get_advertiser_id(advertiser: Advertiser = Depends(get_advertiser)) -> AdvertiserDTO:
    """
    Получение информации о рекламодателе по его ID<br>
    Возвращает `404` если рекламодатель не найден
    """
    return AdvertiserDTO(**advertiser.model_dump())

@router.get("")
async def get_advertisers(
        service: AdvertiserServiceDep,
        data: FindRequest = Query()
) -> GetAdvertisersResponse:
    """
    Получение списка рекламодателей, отсортированного по убыванию даты создания (системной)
    """
    advertisers, total = await service.get_all(data.size, data.page - 1)
    return GetAdvertisersResponse(
        total_pages = math.ceil(total / data.size),
        current_page = data.page,
        advertisers = [AdvertiserDTO(**advertiser.model_dump()) for advertiser in advertisers]
    )

@router.post("/bulk", status_code=201)
async def bulk_create(
        data: list[AdvertiserDTO],
        service: AdvertiserServiceDep
    ) -> list[AdvertiserDTO]:
    """
    Создаёт новых или обновляет существующих рекламодателей
    """
    if not data:
        return []
    data = remove_duplicated_ids(data, "advertiser_id")
    await service.bulk_insert(data)
    return data