import uuid
from typing import Annotated, Callable, Any

from fastapi import Depends
from sqlalchemy import func, case, desc, Float
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.db import SessionDep
from src.core.utils import get_current_day, merge_stat_res
from src.models import ClientAdvertiserScore, Client
from src.models.campaign import Campaign


__all__ = ("CampaignRepository", "CampaignRepoDep")

from src.models.client_adv_actions import ClientViewCampaign, ClientClickCampaign


class CampaignRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_viewed_by_client(self, client_id: uuid.UUID, campaign_id: uuid.UUID) -> bool:
        return await self.session.scalar(
            select(True).select_from(ClientViewCampaign).where(
                (ClientViewCampaign.client_id == client_id) & (ClientViewCampaign.campaign_id == campaign_id)
            )
        ) or False

    async def get_by_id(self, campaign_id: uuid.UUID) -> Campaign | None:
        return await self.session.scalar(
            select(Campaign).filter(Campaign.campaign_id == campaign_id)
        )

    async def get_by_advertiser(self, advertiser_id: uuid.UUID, size: int, page: int) -> tuple[list[Campaign], int]:
        stmt = select(Campaign).filter(Campaign.advertiser_id == advertiser_id).order_by(Campaign.created_at.desc())
        total_count = await self.session.scalar(select(func.count()).select_from(stmt.subquery()))
        result = await self.session.scalars(stmt.limit(size).offset(size * page))
        return result.all(), total_count

    async def get_client_ad(self, client_id: uuid.UUID) -> Campaign | None:
        current_day = await get_current_day()
        view_query_factory = lambda res: select(res).select_from(ClientViewCampaign).filter(
                (ClientViewCampaign.campaign_id == Campaign.campaign_id) &
                (ClientViewCampaign.client_id == Client.client_id)
            ).scalar_subquery()
        stmt = (select(Campaign)
            .join(Client, Client.client_id == client_id)
            .join(ClientAdvertiserScore,
                (Campaign.advertiser_id == ClientAdvertiserScore.advertiser_id) &
                (client_id == ClientAdvertiserScore.client_id), isouter=True
            )
            .order_by(desc(
                (
                    (
                        func.greatest(func.coalesce(ClientAdvertiserScore.score, 0) /
                            func.coalesce(
                                select(func.percentile_cont(0.9).within_group(ClientAdvertiserScore.score.asc()))
                                .select_from(ClientAdvertiserScore)
                                .scalar_subquery(),
                                1
                        ), 0.1) * Campaign.cost_per_click
                    ) + case((view_query_factory(True) == True, 0), else_=Campaign.cost_per_impression)
                ) * func.coalesce(
                    view_query_factory(1 / (2 * func.cast(select(
                        func.greatest(
                            func.max(Campaign.cost_per_click),
                            func.max(Campaign.cost_per_impression)
                        )
                    ).scalar_subquery(), Float))),
                    1
                )
            ))
            .filter(
                (select(func.count()).select_from(ClientClickCampaign).where(
                    (ClientClickCampaign.campaign_id == Campaign.campaign_id) &
                    (ClientClickCampaign.client_id == Client.client_id)
                ).scalar_subquery() == 0) & # Check is not clicked
                (current_day >= Campaign.start_date) & (current_day <= Campaign.end_date) &
                case((
                        (Campaign.target_gender != None) & (Campaign.target_gender != "ALL"), Campaign.target_gender == Client.gender
                    ),
                    else_=True
                ) &
                case((Campaign.target_location != None, Campaign.target_location == Client.location), else_=True) &
                case((Campaign.target_age_from != None, Client.age >= Campaign.target_age_from), else_=True) &
                case((Campaign.target_age_to != None, Client.age <= Campaign.target_age_to), else_=True) &
                (select(func.count())
                    .select_from(ClientViewCampaign)
                    .where(ClientViewCampaign.campaign_id == Campaign.campaign_id)
                .scalar_subquery() < Campaign.impressions_limit * 1.03)
            )
            .limit(1)
        )
        ad = await self.session.scalar(stmt)
        if ad:
            await self.session.exec(insert(ClientViewCampaign).values(
                client_id=client_id,
                campaign_id=ad.campaign_id,
                date=current_day,
                cost=ad.cost_per_impression,
            ).on_conflict_do_nothing())
        return ad

    async def _build_stat_query(
        self,
        filter: Callable[[type[SQLModel]], Any], # Sample of filter: lambda x: x.campaign_id == campaign_id
        group_date: bool = False
    ) -> tuple[list[tuple], list[tuple]]:
        stmt_view = (
            select(func.count(), func.sum(ClientViewCampaign.cost))
            .select_from(ClientViewCampaign)
            .join(Campaign, Campaign.campaign_id == ClientViewCampaign.campaign_id)
            .filter(filter(ClientViewCampaign))
        )
        stmt_click = (
            select(func.count(), func.sum(ClientClickCampaign.cost))
            .select_from(ClientClickCampaign)
            .join(Campaign, Campaign.campaign_id == ClientClickCampaign.campaign_id)
            .filter(filter(ClientClickCampaign))
        )
        if group_date:
            stmt_view = stmt_view.add_columns(ClientViewCampaign.date).group_by(ClientViewCampaign.date)
            stmt_click = stmt_click.add_columns(ClientClickCampaign.date).group_by(ClientClickCampaign.date)
        return (await self.session.exec(stmt_view)).fetchall(), (await self.session.exec(stmt_click)).fetchall()

    async def get_stat_by_campaign(self, campaign_id: uuid.UUID) -> tuple[int]:
        """
        Получение статистики по отдельной кампании
        Return:
            tuple[view_count, view_cost, click_count, click_cost]
        """
        view, click = await self._build_stat_query(lambda x: x.campaign_id == campaign_id)
        return *view[0], *click[0]

    async def get_stat_by_advertiser(self, advertiser_id: uuid.UUID) -> tuple[int]:
        """
        Получение статистики по рекламодателю
        Return:
            tuple[view_count, view_cost, click_count, click_cost]
        """
        view, click = await self._build_stat_query(lambda x: Campaign.advertiser_id == advertiser_id)
        return *view[0], *click[0]

    async def get_stat_by_advertiser_day(self, advertiser_id: uuid.UUID) -> tuple[int]:
        """
        Получение статистики по рекламодателю по дням
        Return:
            list[tuple[view_count, view_cost, click_count, click_cost, date]]
        """
        data = await self._build_stat_query(lambda x: Campaign.advertiser_id == advertiser_id, True)
        return merge_stat_res(data[0], data[1])

    async def get_stat_by_campaign_day(self, campaign_id: uuid.UUID) -> tuple[int]:
        """
        Получение статистики по отдельной кампании по дням
        Return:
            list[tuple[view_count, view_cost, click_count, click_cost, date]]
        """
        data = await self._build_stat_query(lambda x: x.campaign_id == campaign_id, True)
        return merge_stat_res(data[0], data[1])

    async def insert_ad_click(self, client_id: uuid.UUID, campaign: Campaign) -> None:
        await self.session.exec(insert(ClientClickCampaign).values(
            client_id=client_id,
            campaign_id=campaign.campaign_id,
            date=await get_current_day(),
            cost=campaign.cost_per_click,
        ).on_conflict_do_nothing())

    async def insert(self, campaign: Campaign) -> Campaign:
        self.session.add(campaign)
        await self.session.flush()
        await self.session.refresh(campaign)
        return campaign

    async def delete(self, campaign: Campaign) -> None:
        await self.session.delete(campaign)

def create_campaign_repository(session: SessionDep) -> CampaignRepository:
    return CampaignRepository(session)

CampaignRepoDep = Annotated[CampaignRepository, Depends(create_campaign_repository)]