from pydantic import BaseModel


__all__ = ("UploadFileResponse",)


class UploadFileResponse(BaseModel):
    file_id: str
    image_url: str