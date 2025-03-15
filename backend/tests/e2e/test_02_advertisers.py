import uuid

import pytest

from tests.conftest import test_client, create_client, create_advertiser


async def test_bulk(test_client):
    # Базовая проверка работы
    uuid1 = str(uuid.uuid4())
    uuid2 = str(uuid.uuid4())
    advertisers = [
        {
            "advertiser_id": uuid1,
            "name": "Test Corp",
        },
        {
            "advertiser_id": uuid2,
            "name": "Zoom Corp",
        },
    ]

    response = await test_client.post('/advertisers/bulk', json=advertisers)
    assert response.status_code == 201
    assert response.json() == advertisers

    # Из двух объектов с 1 ID будет считаться последний
    advertisers[1] = advertisers[0]
    advertisers[1]['name'] = 'Test 2'
    response = await test_client.post('/advertisers/bulk', json=advertisers)
    assert response.status_code == 201
    assert response.json() == advertisers[1:]

    # Пустой массив
    response = await test_client.post('/advertisers/bulk', json=[])
    assert response.status_code == 201
    assert response.json() == []

    # Неполный объект
    response = await test_client.post('/advertisers/bulk', json=[{
        "advertiser_id": uuid1
    }])
    assert response.status_code == 422

async def test_get(test_client):
    # Создаём рекламодателя
    uuid1 = str(uuid.uuid4())
    advertiser = {
        "advertiser_id": uuid1,
        "name": "Test Corp"
    }
    response = await test_client.post('/advertisers/bulk', json=[advertiser])
    assert response.status_code == 201

    # Получаем рекламодателя
    response = await test_client.get(f'/advertisers/{uuid1}')
    assert response.status_code == 200
    assert response.json() == advertiser

    # Получение несуществующего рекламодателя
    response = await test_client.get(f'/advertisers/{uuid.uuid4()}')
    assert response.status_code == 404

async def test_ml_score(test_client):
    client_id = await create_client(test_client)
    advertiser_id = await create_advertiser(test_client)

    # Обновление ML Score
    response = await test_client.post(f'/ml-scores', json={
        "client_id": client_id,
        "advertiser_id": advertiser_id,
        "score": 5
    })
    assert response.status_code == 200

    # Повторное обновление ML Score
    response = await test_client.post(f'/ml-scores', json={
        "client_id": client_id,
        "advertiser_id": advertiser_id,
        "score": 10
    })
    assert response.status_code == 200