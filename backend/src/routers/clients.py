from fastapi import APIRouter, Depends

from src.core.exc import NotFoundError, HTTPErrorModel
from src.core.utils import remove_duplicated_ids
from src.models import Client
from src.schemes import ClientDTO
from src.service.client import ClientServiceDep, get_client


router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("/random", include_in_schema=False)
async def get_random_client(service: ClientServiceDep) -> ClientDTO:
    """
    Получение случайного клиента<br>
    Необходимо исключительно для интерактивного просмотра рекламы в тг боте
    """
    client = await service.get_random()
    if not client:
        raise NotFoundError("No clients available")
    return ClientDTO(**client.model_dump())

@router.get(
    "/{client_id}",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Клиент не найден"
        }
    }
)
async def get_client_info(client: Client = Depends(get_client)) -> ClientDTO:
    """
    Получение информации о клиенте по его ID<br>
    Возвращает `404` в случае если клиент не найден
    """
    return ClientDTO(**client.model_dump())

@router.post("/bulk", status_code=201)
async def bulk_create(data: list[ClientDTO], service: ClientServiceDep) -> list[ClientDTO]:
    """
    Создаёт новых или обновляет существующих клиентов<br>
    """
    if not data:
        return []
    data = remove_duplicated_ids(data, "client_id")
    await service.bulk_insert(data)
    return data