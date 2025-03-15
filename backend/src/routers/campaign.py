import math
import uuid

from fastapi import APIRouter, Depends, Query

from src.core.exc import HTTPErrorModel
from src.models import Advertiser, Campaign
from src.schemes import CampaignDTO, BaseCampaignDTO, FindRequest, GetCampaignsResponse, \
    GenerateAdvertResponse, GenerateAdvertRequest
from src.schemes.campaign import EditCampaignRequestPatch
from src.service.advertiser import get_advertiser
from src.service.campaign import CampaignServiceDep, get_campaign
from src.service.gpt import GPTServiceDep

router = APIRouter(prefix="/advertisers/{advertiser_id}/campaigns", tags=["Campaigns"])


@router.get(
    "/{campaign_id}",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламная кампания не найдена"
        }
    }
)
async def get_campaign_info(campaign: Campaign = Depends(get_campaign)) -> CampaignDTO:
    """
    Получение информации о кампании<br>
    Возвращает `404` если компания не найдена
    """
    return CampaignDTO.from_db(campaign)

@router.post(
    "",
    status_code=201,
    responses={
        403: {
            "model": HTTPErrorModel,
            "description": "Неэтичная рекламная кампания"
        },
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламодатель не найден"
        }
    }
)
async def new_campaign(
        data: BaseCampaignDTO,
        service: CampaignServiceDep,
        advertiser_id: uuid.UUID
) -> CampaignDTO:
    """
    Создание новой рекламной кампании<br>
    Возвращает `422` если передано неверное изображение (получать в /files)<br>
    Возвращает `403` если текст или название рекламной кампании не является этичным (при включённом /security/moderation)<br>
    Возвращает `404` если рекламодатель не найден
    """
    return CampaignDTO.from_db(await service.insert(advertiser_id, data))

@router.patch(
    "/{campaign_id}",
    responses={
        403: {
            "model": HTTPErrorModel,
            "description": "Неэтичная рекламная кампания / Кампания уже началась"
        },
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламная кампания не найдена"
        }
    }
)
async def edit_campaign_patch(
        data: EditCampaignRequestPatch,
        service: CampaignServiceDep,
        campaign: Campaign = Depends(get_campaign)
) -> CampaignDTO:
    """
    Обновляет параметры рекламной кампании. Обновляет параметры независимо.
    После старта кампании невозможно изменить такие параметры как: *_limit, *_date<br>
    После конца кампании изменять нельзя никакие параметры<br>
    Возвращает `422` если передано неверное изображение (получать в /files)<br>
    Возвращает `403` если текст или название рекламной кампании не является этичным (при включённом /security/moderation)
    или редактирование происходит после начала рекламной кампании<br>
    Возвращает `404` если кампания не найдена
    """
    await service.update(campaign, data)
    return CampaignDTO.from_db(campaign)

@router.put(
    "/{campaign_id}",
    responses={
        403: {
            "model": HTTPErrorModel,
            "description": "Неэтичная рекламная кампания / Кампания уже началась"
        },
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламная кампания не найдена"
        }
    }
)
async def edit_campaign_put(
        data: BaseCampaignDTO,
        service: CampaignServiceDep,
        campaign: Campaign = Depends(get_campaign)
) -> CampaignDTO:
    """
    Обновляет параметры рекламной кампании. В отличие от PATCH варианта заменяет весь объект<br>
    После старта кампании невозможно изменить такие параметры как: *_limit, *_date<br>
    После конца кампании изменять нельзя никакие параметры<br>
    Возвращает `422` если передано неверное изображение (получать в /files)<br>
    Возвращает `403` если текст или название рекламной кампании не является этичным (при включённом /security/moderation)
    или редактирование происходит после начала рекламной кампании<br>
    Возвращает `404` если кампания не найдена
    """
    await service.update(campaign, data)
    return CampaignDTO.from_db(campaign)

@router.delete(
    "/{campaign_id}",
    status_code=204,
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламная кампания не найдена"
        }
    }
)
async def delete_campaign(
        service: CampaignServiceDep,
        campaign: Campaign = Depends(get_campaign)
    ):
    """
    Удаление рекламной кампании<br>
    Возвращает `404` если кампания не найдена
    """
    await service.delete(campaign)

@router.get(
    "",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламодатель не найден"
        }
    }
)
async def get_campaigns(
        service: CampaignServiceDep,
        data: FindRequest = Query(),
        advertiser: Advertiser = Depends(get_advertiser)
) -> GetCampaignsResponse:
    """
    Получение списка рекламных кампаний рекламодателя, отсортированного по убыванию даты создания (системной)<br>
    Возвращает `404` если рекламодатель не найден
    """
    campaigns, total = await service.get_by_advertiser(advertiser.advertiser_id, data.size, data.page - 1)
    return GetCampaignsResponse(
        total_pages = math.ceil(total / data.size),
        current_page = data.page,
        campaigns = [CampaignDTO.from_db(campaign) for campaign in campaigns]
    )

@router.post(
    "/generate",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламодатель не найден"
        }
    }
)
async def generate_ad(
        data: GenerateAdvertRequest,
        service: GPTServiceDep,
        advertiser: Advertiser = Depends(get_advertiser)
) -> GenerateAdvertResponse:
    """
    Генерация рекламного текста при помощи ИИ на основе имени рекламодателя и названия рекламной кампании<br.
    Возвращает `404` если рекламодатель не найден
    """
    return GenerateAdvertResponse(
        ad_text=await service.generate_ad_text(data.ad_title, advertiser.name, data.size),
    )