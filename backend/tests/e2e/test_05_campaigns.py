import uuid

import pytest

from tests.conftest import create_advertiser, create_campaign


async def test_create(test_client):
    advertiser_id = await create_advertiser(test_client)

    campaign = {
        "impressions_limit": 1000,
        "clicks_limit": 100,
        "cost_per_impression": 10,
        "cost_per_click": 100,
        "ad_title": "Test Title",
        "ad_text": "Test Test!",
        "start_date": 15,
        "end_date": 30,
        "targeting": {}
    }

    # Базовое добавление
    response = await test_client.post(f'/advertisers/{advertiser_id}/campaigns', json=campaign)
    assert response.status_code == 201

    created_campaign = response.json()
    campaign.update({
        "campaign_id": created_campaign["campaign_id"],
        "advertiser_id": advertiser_id,
        "ad_image_id": None,
        "ad_image_url": None,
        "targeting": created_campaign["targeting"],
    })
    assert created_campaign == campaign

    # Неверный advertiser_id
    response = await test_client.post(f'/advertisers/{str(uuid.uuid4())}/campaigns', json=campaign)
    assert response.status_code == 404

    # Неверный image_id
    campaign['ad_image_id'] = "123"
    response = await test_client.post(f'/advertisers/{advertiser_id}/campaigns', json=campaign)
    assert response.status_code == 422

    # Добавление с верным image_id
    response = await test_client.post('/files', files={"file": open("tests/icon.png", "rb")})
    assert response.status_code == 200
    campaign['ad_image_id'] = response.json()["file_id"]

    response = await test_client.post(f'/advertisers/{advertiser_id}/campaigns', json=campaign)
    assert response.status_code == 201

    # Ненормативная лексика в тексте
    # campaign['ad_image_id'] = None
    # campaign['ad_text'] = "Продажа наркотиков и прочих запрещённых веществ"
    # response = await test_client.post(f'/advertisers/{advertiser_id}/campaigns', json=campaign)
    # assert response.status_code == 403

async def test_get(test_client):
    campaign = await create_campaign(test_client)

    # Базовая проверка получения кампании
    response = await test_client.get(f'/advertisers/{campaign['advertiser_id']}/campaigns/{campaign["campaign_id"]}')
    assert response.status_code == 200
    assert response.json() == campaign

    # Получение неверной кампании
    response = await test_client.get(f'/advertisers/{campaign['advertiser_id']}/campaigns/{str(uuid.uuid4())}')
    assert response.status_code == 404

async def test_update(test_client):
    campaign = await create_campaign(test_client)

    # Базовое изменение
    campaign['cost_per_click'] = 999
    response = await test_client.put(
        f'/advertisers/{campaign['advertiser_id']}/campaigns/{campaign["campaign_id"]}',
        json=campaign
    )
    assert response.status_code == 200
    assert response.json() == campaign

    # Изменение с неверным изображением
    campaign['ad_image_id'] = "123"
    response = await test_client.put(
        f'/advertisers/{campaign['advertiser_id']}/campaigns/{campaign["campaign_id"]}',
        json=campaign
    )
    assert response.status_code == 422
    campaign['ad_image_id'] = None

    # Изменение кампании методом PATCH
    response = await test_client.patch(
        f'/advertisers/{campaign['advertiser_id']}/campaigns/{campaign["campaign_id"]}',
        json={"ad_title": "Test PATCH"}
    )
    assert response.status_code == 200

    # Смена времени
    response = await test_client.post("/time/advance", json={"current_date": 15})
    assert response.status_code == 200

    # Попытка изменить кампанию после старта (успешно)
    campaign['ad_title'] = "Test Title"
    response = await test_client.put(
        f'/advertisers/{campaign['advertiser_id']}/campaigns/{campaign["campaign_id"]}',
        json=campaign
    )
    assert response.status_code == 200

    # Попытка изменить кампанию после старта (неуспешно)
    campaign['end_date'] = 100
    response = await test_client.put(
        f'/advertisers/{campaign['advertiser_id']}/campaigns/{campaign["campaign_id"]}',
        json=campaign
    )
    assert response.status_code == 403

async def test_get_campaigns(test_client):
    campaign = await create_campaign(test_client)
    campaign_2 = await create_campaign(test_client, campaign['advertiser_id'])
    campaign_3 = await create_campaign(test_client, campaign['advertiser_id'])

    # Базовая проверка поиска
    response = await test_client.get(
        f"/advertisers/{campaign['advertiser_id']}/campaigns",
        params={"size": 2}
    )
    assert response.status_code == 200
    assert response.json() == {
        "total_pages": 2,
        "current_page": 1,
        "campaigns": [
            campaign_3,
            campaign_2
        ]
    }

    # Проверка работы страниц
    response = await test_client.get(
        f"/advertisers/{campaign['advertiser_id']}/campaigns",
        params={"size": 2, "page": 2}
    )
    assert response.status_code == 200
    assert response.json() == {
        "total_pages": 2,
        "current_page": 2,
        "campaigns": [
            campaign
        ]
    }

async def test_delete(test_client):
    campaign = await create_campaign(test_client)

    # Удаление кампании
    response = await test_client.delete(f"/advertisers/{campaign['advertiser_id']}/campaigns/{campaign['campaign_id']}")
    assert response.status_code == 204

    # Проверка, что кампания действительно удалена
    response = await test_client.get(f"/advertisers/{campaign['advertiser_id']}/campaigns/{campaign['campaign_id']}")
    assert response.status_code == 404