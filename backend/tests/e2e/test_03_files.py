async def test_upload(test_client):
    # Загрузка валидного изображения
    response = await test_client.post('/files', files={'file': open("tests/icon.png", "rb")})
    assert response.status_code == 200
    file_id = response.json()['file_id']

    # Получение изображения
    response = await test_client.get(f'/files/{file_id}')
    assert response.status_code == 200

    # Загрузка невалидного изображения
    response = await test_client.post('/files', files={'file': b"PROOOOD"})
    assert response.status_code == 422