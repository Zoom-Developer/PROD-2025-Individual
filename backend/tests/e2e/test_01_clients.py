import uuid


async def test_bulk(test_client):
    # Базовая проверка работы
    uuid1 = str(uuid.uuid4())
    uuid2 = str(uuid.uuid4())
    clients = [
        {
            "client_id": uuid1,
            "login": "zoomdevs",
            "age": 18,
            "location": "Moscow",
            "gender": "MALE"
        },
        {
            "client_id": uuid2,
            "login": "testuser",
            "age": 23,
            "location": "Izhevsk",
            "gender": "FEMALE"
        }
    ]

    response = await test_client.post('/clients/bulk', json=clients)
    assert response.status_code == 201
    assert response.json() == clients

    # Из двух объектов с 1 ID будет считаться последний
    clients[1] = clients[0]
    clients[1]['age'] = 24
    response = await test_client.post('/clients/bulk', json=clients)
    assert response.status_code == 201
    assert response.json() == clients[1:]

    # Пустой массив
    response = await test_client.post('/clients/bulk', json=[])
    assert response.status_code == 201
    assert response.json() == []

    # Неполный объект
    response = await test_client.post('/clients/bulk', json=[{
        "client_id": uuid1,
        "login": "zoomdevs",
    }])
    assert response.status_code == 422

    # Отрицательный возраст
    clients[0]['age'] = -1
    response = await test_client.post('/clients/bulk', json=[clients[0]])
    assert response.status_code == 422

async def test_get(test_client):
    # Создаём клиента
    uuid1 = str(uuid.uuid4())
    client = {
        "client_id": uuid1,
        "login": "testuser",
        "age": 23,
        "location": "Moscow",
        "gender": "MALE"
    }
    response = await test_client.post('/clients/bulk', json=[client])
    assert response.status_code == 201

    # Получаем клиента
    response = await test_client.get(f'/clients/{uuid1}')
    assert response.status_code == 200
    assert response.json() == client

    # Получение несуществующего клиента
    response = await test_client.get(f'/clients/{uuid.uuid4()}')
    assert response.status_code == 404