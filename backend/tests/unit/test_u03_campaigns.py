import uuid

from src.core.exc import NotFoundError, ValidationError
from src.schemes import AdvertiserDTO, BaseCampaignDTO, CampaignTargetDTO, EditCampaignRequestPatch


async def create_advertiser(service):
    advertiser = AdvertiserDTO(
        advertiser_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
        name="Test Corp"
    )
    return (await service.bulk_insert([advertiser]))[0]

async def create_campaign(service, advertiser_id):
    campaign = BaseCampaignDTO(
        impressions_limit=1000,
        clicks_limit=100,
        cost_per_impression=10.0,
        cost_per_click=100.0,
        ad_title="Test Title",
        ad_text="Test Text!",
        start_date=15,
        end_date=30,
        targeting=CampaignTargetDTO()
    )
    return await service.insert(advertiser_id, campaign)

# TESTS

async def test_create(campaign_service, advertiser_service):
    advertiser = await create_advertiser(advertiser_service)
    campaign = BaseCampaignDTO(
        impressions_limit=1000,
        clicks_limit=100,
        cost_per_impression=10.0,
        cost_per_click=100.0,
        ad_title="Test Title",
        ad_text="Test Test!",
        start_date=15,
        end_date=30,
        targeting=CampaignTargetDTO()
    )

    res = await campaign_service.insert(advertiser.advertiser_id, campaign)
    assert res.ad_title == campaign.ad_title
    assert res.ad_text == campaign.ad_text

    # Неверный advertiser_id
    try:
        await campaign_service.insert(uuid.uuid4(), campaign)
        assert False
    except NotFoundError:
        pass

    # Неверный image_id
    campaign.ad_image_id = "123"
    try:
        await campaign_service.insert(advertiser.advertiser_id, campaign)
        assert False
    except ValidationError:
        pass

async def test_get(campaign_service, advertiser_service):
    advertiser = await create_advertiser(advertiser_service)
    campaign = await create_campaign(campaign_service, advertiser.advertiser_id)

    res = await campaign_service.get_by_id(campaign.campaign_id)
    assert campaign.model_dump() == res.model_dump()

    # Неверный campaign_id
    res = await campaign_service.get_by_id(uuid.uuid4())
    assert res is None

async def test_update(campaign_service, advertiser_service):
    advertiser = await create_advertiser(advertiser_service)
    campaign = await create_campaign(campaign_service, advertiser.advertiser_id)

    updated_data = BaseCampaignDTO(
        impressions_limit=2000,
        clicks_limit=200,
        cost_per_impression=20.0,
        cost_per_click=200.0,
        ad_title="Updated Title",
        ad_text="Updated Text!",
        start_date=15,
        end_date=30,
        targeting=CampaignTargetDTO()
    )

    await campaign_service.update(campaign, updated_data)
    updated_campaign = await campaign_service.get_by_id(campaign.campaign_id)

    assert updated_campaign.impressions_limit == updated_data.impressions_limit
    assert updated_campaign.clicks_limit == updated_data.clicks_limit
    assert updated_campaign.cost_per_impression == updated_data.cost_per_impression
    assert updated_campaign.cost_per_click == updated_data.cost_per_click
    assert updated_campaign.ad_title == updated_data.ad_title
    assert updated_campaign.ad_text == updated_data.ad_text

    # Неверные данные для обновления
    invalid_data = EditCampaignRequestPatch(
        start_date=10,
        end_date=5
    )

    try:
        await campaign_service.update(campaign, invalid_data)
        assert False
    except ValidationError:
        pass


async def test_delete(campaign_service, advertiser_service):
    advertiser = await create_advertiser(advertiser_service)
    campaign = await create_campaign(campaign_service, advertiser.advertiser_id)

    await campaign_service.delete(campaign)

    res = await campaign_service.get_by_id(campaign.campaign_id)
    assert res is None