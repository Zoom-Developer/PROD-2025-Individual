async def test_time(test_client):
    # Базовая установка времени
    response = await test_client.post('/time/advance', json={"current_date": 10})
    assert response.status_code == 200

    # Установка неправильного времени
    response = await test_client.post('/time/advance', json={"current_date": "XXX"})
    assert response.status_code == 422

    # Установка времени в прошлом
    response = await test_client.post('/time/advance', json={"current_date": 1})
    assert response.status_code == 422