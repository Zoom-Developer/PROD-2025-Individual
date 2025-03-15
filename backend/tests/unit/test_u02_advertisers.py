import uuid

import pytest

from src.core.exc import NotFoundError
from src.models import Advertiser
from src.schemes import AdvertiserDTO, ClientDTO


@pytest.mark.parametrize("advertisers", [
    [AdvertiserDTO(
        advertiser_id="27f3423c-b3f9-4109-8fe5-c7a54b693408",
        name="Test Corp"
    )],
    [
        AdvertiserDTO(
            advertiser_id="74b51da1-ba6f-4652-ae01-ae4d97a02448",
            name="Another Corp"
        ),
        AdvertiserDTO(
            advertiser_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
            name="Third Corp"
        ),
    ],
])
async def test_valid_bulk(advertiser_service, advertisers):
    res = await advertiser_service.bulk_insert(advertisers)
    assert all([isinstance(a, Advertiser) for a in res])
    assert [a.model_dump() in res for a in res] == [a.model_dump() in advertisers for a in advertisers]

async def test_get(advertiser_service):
    advertiser = AdvertiserDTO(
        advertiser_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
        name="Test Corp"
    )
    await advertiser_service.bulk_insert([advertiser])

    # Получение существующего рекламодателя
    res = await advertiser_service.get_by_id("abd46d85-d553-4c9d-9a34-d64a56ca19d7")
    adv_dump = advertiser.model_dump()
    adv_dump['created_at'] = res.created_at
    assert res.model_dump() == adv_dump

    # Получение несуществующего рекламодателя
    res = await advertiser_service.get_by_id(uuid.uuid4())
    assert res is None

async def test_update(advertiser_service):
    advertiser = AdvertiserDTO(
        advertiser_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
        name="Test Corp"
    )
    await advertiser_service.bulk_insert([advertiser])

    advertiser.name = "Updated Corp"
    res = await advertiser_service.bulk_insert([advertiser])
    assert res[0].name == advertiser.name

    res = await advertiser_service.get_by_id("abd46d85-d553-4c9d-9a34-d64a56ca19d7")
    assert res.name == advertiser.name

async def test_score(advertiser_service, client_service):
    client = ClientDTO(
        client_id="abd46d85-d553-4c9d-9a34-d64a56ca19d7",
        login="test@mail.ru",
        age=20,
        location="Moscow",
        gender="MALE"
    )
    advertiser = AdvertiserDTO(
        advertiser_id="692947ef-8f23-4b93-ae58-da240cb9ae0a",
        name="Test Corp"
    )
    await advertiser_service.bulk_insert([advertiser])
    await client_service.bulk_insert([client])

    # Выдача ML Score
    await advertiser_service.update_score(client.client_id, advertiser.advertiser_id, 5)

    # Повторная выдача ML Score
    await advertiser_service.update_score(client.client_id, advertiser.advertiser_id, 10)

    # Неверный client_id
    try:
        await advertiser_service.update_score(uuid.uuid4(), advertiser.advertiser_id, 10)
        assert False
    except NotFoundError:
        pass

    # Неверный advertiser_id
    try:
        await advertiser_service.update_score(client.client_id, uuid.uuid4(), 10)
        assert False
    except NotFoundError:
        pass