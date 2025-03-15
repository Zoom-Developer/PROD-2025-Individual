from fastapi import APIRouter, Depends

from src.core.exc import HTTPErrorModel
from src.models import Campaign, Advertiser
from src.schemes import CampaignStat, CampaignStatDay
from src.service.advertiser import get_advertiser
from src.service.campaign import get_ad, CampaignServiceDep

router = APIRouter(prefix="/stats", tags=["Statistic"])

@router.get(
    "/campaigns/{campaign_id}",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламная кампания не найдена"
        }
    }
)
async def get_stat_campaign(service: CampaignServiceDep, campaign: Campaign = Depends(get_ad)) -> CampaignStat:
    """
    Статистика рекламной кампании за всё время<br>
    Возвращает `404` если компания не найдена
    """
    stat = await service.get_stat_by_campaign(campaign.campaign_id)
    return CampaignStat(
        impressions_count=stat[0],
        spent_impressions=stat[1] or 0,
        clicks_count=stat[2],
        spent_clicks=stat[3] or 0
    )

@router.get(
    "/advertisers/{advertiser_id}/campaigns",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламодатель не найден"
        }
    }
)
async def get_stat_advertiser(service: CampaignServiceDep, advertiser: Advertiser = Depends(get_advertiser)) -> CampaignStat:
    """
    Статистика рекламодателя за всё время<br>
    Возвращает `404` если рекламодатель не найден
    """
    stat = await service.get_stat_by_advertiser(advertiser.advertiser_id)
    return CampaignStat(
        impressions_count=stat[0],
        spent_impressions=stat[1] or 0,
        clicks_count=stat[2],
        spent_clicks=stat[3] or 0
    )

@router.get(
    "/campaigns/{campaign_id}/daily",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламная кампания не найдена"
        }
    }
)
async def get_stat_campaign_daily(service: CampaignServiceDep, campaign: Campaign = Depends(get_ad)) -> list[CampaignStatDay]:
    """
    Статистика рекламной кампании по дням (сортировка по возрастанию дня)<br>
    Возвращает `404` если кампания не найдена
    """
    stat = await service.get_stat_by_campaign_day(campaign.campaign_id)
    return [CampaignStatDay(
        impressions_count=day[0],
        spent_impressions=day[1] or 0,
        clicks_count=day[2],
        spent_clicks=day[3] or 0,
        day=day[4]
    ) for day in stat]

@router.get(
    "/advertisers/{advertiser_id}/campaigns/daily",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Рекламодатель не найден"
        }
    }
)
async def get_stat_advertiser_daily(service: CampaignServiceDep, advertiser: Advertiser = Depends(get_advertiser)) -> list[CampaignStatDay]:
    """
    Статистика рекламодателя по дням (сортировка по возрастанию дня)<br>
    Возвращает `404` если рекламодатель не найден
    """
    stat = await service.get_stat_by_advertiser_day(advertiser.advertiser_id)
    return [CampaignStatDay(
        impressions_count=day[0],
        spent_impressions=round(day[1] or 0, 2),
        clicks_count=day[2],
        spent_clicks=round(day[3] or 0, 2),
        day=day[4]
    ) for day in stat]