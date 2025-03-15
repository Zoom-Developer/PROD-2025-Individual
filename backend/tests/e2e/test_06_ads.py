import uuid

import pytest

from tests.conftest import create_advertiser, create_campaign, create_client


async def test_show_ad(test_client):
    client_id = await create_client(test_client)

    # Получение рекламы без реклам
    response = await test_client.get("/ads", params={"client_id": client_id})
    assert response.status_code == 404

    # Получение неактивной рекламы

    await create_campaign(test_client)

    response = await test_client.get("/ads", params={"client_id": client_id})
    assert response.status_code == 404

    # Базовое получение рекламы
    await test_client.post("/time/advance", json={"current_date": 15})

    response = await test_client.get("/ads", params={"client_id": client_id})
    assert response.status_code == 200

async def test_click_ad(test_client):
    client_id = await create_client(test_client)
    campaign = await create_campaign(test_client)
    await test_client.post("/time/advance", json={"current_date": 15})

    # Базовый клик по рекламе
    response = await test_client.get("/ads", params={"client_id": client_id})
    assert response.status_code == 200

    response = await test_client.post(f"/ads/{campaign['campaign_id']}/click", json={"client_id": client_id})
    assert response.status_code == 204

    # Реклама не показывается после клика
    response = await test_client.get("/ads", params={"client_id": client_id})
    assert response.status_code == 404