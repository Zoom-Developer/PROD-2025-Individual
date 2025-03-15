from fastapi import APIRouter, Depends

from src.core.exc import NotFoundError, HTTPErrorModel
from src.models import Client, Campaign
from src.schemes import AdvertDTO, ClickAdvertRequest
from src.service.campaign import CampaignServiceDep, get_ad
from src.service.client import get_client


DUMP_SENT = False


router = APIRouter(prefix="/ads", tags=["Ads"])

@router.get(
    "",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Клиент не найден / нет подходящей рекламы"
        }
    }
)
async def get_ad_feed(service: CampaignServiceDep, client: Client = Depends(get_client)) -> AdvertDTO | None:
    global DUMP_SENT
    """
    Получение рекламного объявления для данного пользователя<br>
    Возвращает `404` если клиент не найден<br>
    Возвращает `404` если нет подходящей рекламы
    """
    ad = await service.get_client_ad(client.client_id)
    if ad:
        return AdvertDTO(
            ad_id=ad.campaign_id,
            ad_title=ad.ad_title,
            ad_text=ad.ad_text,
            ad_image_id=ad.ad_image_id,
            advertiser_id=ad.advertiser_id,
        )
    else:
        raise NotFoundError("No available ads")

@router.post(
    "/{campaign_id}/click",
    status_code=204,
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Реклама не найдена"
        }
    }
)
async def ad_click(
        data: ClickAdvertRequest,
        service: CampaignServiceDep,
        campaign: Campaign = Depends(get_ad),
    ):
    """
    Переход по объявлению<br>
    Возвращает `404` если реклама не найдена<br>
    """
    await service.insert_ad_click(data.client_id, campaign)