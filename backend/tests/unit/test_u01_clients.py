import uuid

import pytest

from src.models import Client
from src.schemes import ClientDTO


@pytest.mark.parametrize("clients", [
    [ClientDTO(
        client_id="27f3423c-b3f9-4109-8fe5-c7a54b693408",
        login="mail@gmail.com",
        age=25,
        location="Moscow",
        gender="MALE"
    )],
    [
        ClientDTO(
            client_id="74b51da1-ba6f-4652-ae01-ae4d97a02448",
            login="test@yandex.ru",
            age=20,
            location="New York",
            gender="MALE"
        ),
        ClientDTO(
            client_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
            login="test2@yandex.ru",
            age=15,
            location="Moscow",
            gender="FEMALE"
        ),
    ],
])
async def test_valid_bulk(client_service, clients):
    res = await client_service.bulk_insert(clients)
    assert all([isinstance(c, Client) for c in res])
    assert [c.model_dump() in res for c in res] == [c.model_dump() in clients for c in clients]

async def test_get(client_service):
    client = ClientDTO(
        client_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
        login="test2@yandex.ru",
        age=15,
        location="Moscow",
        gender="FEMALE"
    )
    await client_service.bulk_insert([client])

    # Получение существующего клиента
    res = await client_service.get_by_id("abd46d85-d553-4c9d-9a34-d64a56ca19d7")
    assert res.model_dump() == client.model_dump()

    # Получение несуществующего клиента
    res = await client_service.get_by_id(uuid.uuid4())
    assert res is None

async def test_update(client_service):
    client = ClientDTO(
        client_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
        login="test2@yandex.ru",
        age=15,
        location="Moscow",
        gender="FEMALE"
    )
    res = await client_service.bulk_insert([client])
    assert res[0].model_dump() == client.model_dump()

    client.age = 16
    res = await client_service.bulk_insert([client])
    assert res[0].age == client.age

    res = await client_service.get_by_id("abd46d85-d553-4c9d-9a34-d64a56ca19d7")
    assert res.age == client.age