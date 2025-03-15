from fastapi import APIRouter, File, Response

from src.config import config
from src.core.exc import HTTPErrorModel
from src.schemes import UploadFileResponse
from src.service.files import FilesServiceDep

router = APIRouter(prefix="/files", tags=["Files"])

@router.post(
    "",
    responses={
        404: {
            "model": HTTPErrorModel,
            "description": "Невалидное изображение"
        }
    }
)
async def upload_file(service: FilesServiceDep, file: bytes = File(...)) -> UploadFileResponse:
    """
    Загрузка изображения на сервер<br>
    Возвращает `422` если файл не является валидным изображением
    """
    filename = await service.upload_file(file)
    return UploadFileResponse(
        file_id=filename,
        image_url=config.api_url + "/files/" + filename
    )

@router.get("/{filename}", include_in_schema=False)
async def download_file(service: FilesServiceDep, filename: str):
    data = await service.download_file(filename)
    return Response(
        content = data,
        media_type = "image/jpeg"
    )