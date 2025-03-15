from httpx import AsyncClient

from tests.conftest import create_client, create_campaign


async def create_viewed_ad(cl: AsyncClient, advertiser_id: str = None, date: int = 15, client_id: str = None) -> tuple[dict, str]:
    client_id = client_id or await create_client(cl)
    campaign = await create_campaign(cl, advertiser_id, date)
    response = await cl.get("/ads", params={"client_id": client_id})
    assert response.status_code == 200
    return campaign, client_id

async def create_clicked_ad(cl: AsyncClient, advertiser_id: str = None, date: int = 15, client_id: str = None) -> tuple[dict, str]:
    campaign, client_id = await create_viewed_ad(cl, advertiser_id, date, client_id)
    await cl.post(f"/ads/{campaign['campaign_id']}/click", json={"client_id": client_id})
    return campaign, client_id

async def test_advertiser(test_client):
    await test_client.post("/time/advance", json={"current_date": 15})
    campaign, client_id = await create_viewed_ad(test_client)

    # Получение статистики после просмотра рекламы
    response = await test_client.get(f"/stats/advertisers/{campaign['advertiser_id']}/campaigns")
    assert response.status_code == 200
    assert response.json() == {
        "impressions_count": 1,
        "clicks_count": 0,
        "conversion": 0,
        "spent_impressions": 10,
        "spent_clicks": 0,
        "spent_total": 10
    }

    await create_viewed_ad(test_client, campaign["advertiser_id"], client_id=client_id)

    # Получение статистики после второго просмотра рекламы
    response = await test_client.get(f"/stats/advertisers/{campaign['advertiser_id']}/campaigns")
    assert response.status_code == 200
    assert response.json() == {
        "impressions_count": 2,
        "clicks_count": 0,
        "conversion": 0,
        "spent_impressions": 20,
        "spent_clicks": 0,
        "spent_total": 20
    }

    response = await test_client.post(f"/ads/{campaign['campaign_id']}/click", json={"client_id": client_id})
    assert response.status_code == 204

    # Получение статистики после клика по рекламе
    response = await test_client.get(f"/stats/advertisers/{campaign['advertiser_id']}/campaigns")
    assert response.status_code == 200
    assert response.json() == {
        "impressions_count": 2,
        "clicks_count": 1,
        "conversion": 50,
        "spent_impressions": 20,
        "spent_clicks": 100,
        "spent_total": 120
    }

async def test_advertiser_daily(test_client):
    await test_client.post("/time/advance", json={"current_date": 15})
    campaign, client_id = await create_clicked_ad(test_client)

    # Получение статистики после клика
    response = await test_client.get(f"/stats/advertisers/{campaign['advertiser_id']}/campaigns/daily")
    assert response.status_code == 200
    assert response.json() == [{
        "impressions_count": 1,
        "clicks_count": 1,
        "conversion": 100,
        "spent_impressions": 10,
        "spent_clicks": 100,
        "spent_total": 110,
        "day": 15
    }]

    await test_client.post(f"/ads/{campaign['campaign_id']}/click", json={"client_id": client_id})

    # Получение статистики после повторного клика того же клиента
    response = await test_client.get(f"/stats/advertisers/{campaign['advertiser_id']}/campaigns/daily")
    assert response.status_code == 200
    assert response.json() == [{
        "impressions_count": 1,
        "clicks_count": 1,
        "conversion": 100,
        "spent_impressions": 10,
        "spent_clicks": 100,
        "spent_total": 110,
        "day": 15
    }]

    await test_client.post("/time/advance", json={"current_date": 16})
    campaign_2, _ = await create_viewed_ad(test_client, campaign['advertiser_id'], 16, client_id)

    # Получение статистики после просмотра на следующий день
    response = await test_client.get(f"/stats/advertisers/{campaign['advertiser_id']}/campaigns/daily")
    assert response.status_code == 200
    assert response.json() == [
        {
            "impressions_count": 1,
            "clicks_count": 1,
            "conversion": 100,
            "spent_impressions": 10,
            "spent_clicks": 100,
            "spent_total": 110,
            "day": 15
        },
        {
            "impressions_count": 1,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 10,
            "spent_clicks": 0,
            "spent_total": 10,
            "day": 16
        },
    ]

    client_id_3 = await create_client(test_client)
    response = await test_client.patch(f"/advertisers/{campaign['advertiser_id']}/campaigns/{campaign['campaign_id']}",
        json={"cost_per_impression": 20}
    )
    assert response.status_code == 200
    response = await test_client.get("/ads", params={"client_id": client_id_3})
    assert response.status_code == 200

    # Получение статистики после просмотра с изменением цены
    response = await test_client.get(f"/stats/advertisers/{campaign['advertiser_id']}/campaigns/daily")
    assert response.status_code == 200
    assert response.json() == [
        {
            "impressions_count": 1,
            "clicks_count": 1,
            "conversion": 100,
            "spent_impressions": 10,
            "spent_clicks": 100,
            "spent_total": 110,
            "day": 15
        },
        {
            "impressions_count": 2,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 30,
            "spent_clicks": 0,
            "spent_total": 30,
            "day": 16
        },
    ]

async def test_campaign(test_client):
    await test_client.post("/time/advance", json={"current_date": 15})
    campaign, client_id = await create_viewed_ad(test_client)

    # Получение статистики после просмотра рекламы
    response = await test_client.get(f"/stats/campaigns/{campaign['campaign_id']}")
    assert response.status_code == 200
    assert response.json() == {
        "impressions_count": 1,
        "clicks_count": 0,
        "conversion": 0,
        "spent_impressions": 10,
        "spent_clicks": 0,
        "spent_total": 10
    }

    # Проверка, что статистики кампаний независимы
    campaign_2 = await create_campaign(test_client, campaign["advertiser_id"])
    response = await test_client.get(f"/stats/campaigns/{campaign_2['campaign_id']}")
    assert response.status_code == 200
    assert response.json() == {
        "impressions_count": 0,
        "clicks_count": 0,
        "conversion": 0,
        "spent_impressions": 0,
        "spent_clicks": 0,
        "spent_total": 0
    }

    response = await test_client.post(f"/ads/{campaign['campaign_id']}/click", json={"client_id": client_id})
    assert response.status_code == 204

    # Получение статистики после клика по рекламе
    response = await test_client.get(f"/stats/campaigns/{campaign['campaign_id']}")
    assert response.status_code == 200
    assert response.json() == {
        "impressions_count": 1,
        "clicks_count": 1,
        "conversion": 100,
        "spent_impressions": 10,
        "spent_clicks": 100,
        "spent_total": 110
    }

async def test_campaign_daily(test_client):
    await test_client.post("/time/advance", json={"current_date": 15})
    campaign, client_id = await create_clicked_ad(test_client)

    # Получение статистики после клика
    response = await test_client.get(f"/stats/campaigns/{campaign['campaign_id']}/daily")
    assert response.status_code == 200
    assert response.json() == [{
        "impressions_count": 1,
        "clicks_count": 1,
        "conversion": 100,
        "spent_impressions": 10,
        "spent_clicks": 100,
        "spent_total": 110,
        "day": 15
    }]

    await test_client.post(f"/ads/{campaign['campaign_id']}/click", json={"client_id": client_id})

    # Получение статистики после повторного клика того же клиента
    response = await test_client.get(f"/stats/campaigns/{campaign['campaign_id']}/daily")
    assert response.status_code == 200
    assert response.json() == [{
        "impressions_count": 1,
        "clicks_count": 1,
        "conversion": 100,
        "spent_impressions": 10,
        "spent_clicks": 100,
        "spent_total": 110,
        "day": 15
    }]

    await test_client.post("/time/advance", json={"current_date": 16})
    client_id_2 = await create_client(test_client)

    response = await test_client.get("/ads", params={"client_id": client_id_2})
    assert response.status_code == 200

    # Получение статистики после просмотра на следующий день
    response = await test_client.get(f"/stats/campaigns/{campaign['campaign_id']}/daily")
    assert response.status_code == 200
    assert response.json() == [
        {
            "impressions_count": 1,
            "clicks_count": 1,
            "conversion": 100,
            "spent_impressions": 10,
            "spent_clicks": 100,
            "spent_total": 110,
            "day": 15
        },
        {
            "impressions_count": 1,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 10,
            "spent_clicks": 0,
            "spent_total": 10,
            "day": 16
        },
    ]

    client_id_3 = await create_client(test_client)
    response = await test_client.patch(f"/advertisers/{campaign['advertiser_id']}/campaigns/{campaign['campaign_id']}",
        json={"cost_per_impression": 20.01}
    )
    assert response.status_code == 200
    response = await test_client.get("/ads", params={"client_id": client_id_3})
    assert response.status_code == 200

    # Получение статистики после просмотра с изменением цены
    response = await test_client.get(f"/stats/campaigns/{campaign['campaign_id']}/daily")
    assert response.status_code == 200
    assert response.json() == [
        {
            "impressions_count": 1,
            "clicks_count": 1,
            "conversion": 100,
            "spent_impressions": 10,
            "spent_clicks": 100,
            "spent_total": 110,
            "day": 15
        },
        {
            "impressions_count": 2,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 30.01,
            "spent_clicks": 0,
            "spent_total": 30.01,
            "day": 16
        },
    ]

async def test_other_cases(test_client):
    await test_client.post("/time/advance", json={"current_date": 15})
    campaign = await create_campaign(test_client)
    client_id = await create_client(test_client)

    # Проверка того, что нажатие не считается до показа
    response = await test_client.post(f"/ads/{campaign['campaign_id']}/click", json={"client_id": client_id})
    assert response.status_code == 204

    response = await test_client.get(f"/stats/campaigns/{campaign['campaign_id']}")
    assert response.status_code == 200
    assert response.json() == {
        "impressions_count": 0,
        "clicks_count": 0,
        "conversion": 0,
        "spent_impressions": 0,
        "spent_clicks": 0,
        "spent_total": 0,
    }