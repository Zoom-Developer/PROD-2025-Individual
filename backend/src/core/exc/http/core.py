from enum import Enum

from fastapi import Request
from fastapi.responses import JSONResponse

__all__ = ("HTTPError", "HTTPErrorModel", "HTTPValidationErrorModel", "ValidationError", "NotFoundError",
           "ForbiddenError", "BadRequestError")

from pydantic import BaseModel, Field


class HTTPErrorModel(BaseModel):
    code: int
    message: str

class HTTPValidationErrorModel(HTTPErrorModel):
    detail: list[dict] | None = Field(default=None)

class HTTPError(Exception):

    def __init__(
            self,
            http_code: int = 400,
            message: str = None,
            additional: dict | None = None,
            headers: dict[str, str] | None = None,
            commit_db: bool = False
    ) -> None:
        self.http_code = http_code
        self.message = message
        self.additional = additional or {}
        self.headers = headers or {}
        self.commit_db = commit_db

    @staticmethod
    async def handler(_: Request, exc: "HTTPError") -> JSONResponse:
        return JSONResponse(
            content={
                "code": exc.http_code,
                **({"message": exc.message} if exc.message else {}),
                **exc.additional
            },
            status_code=exc.http_code,
            headers=exc.headers
        )

class BadRequestError(HTTPError):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(400, message)

class ValidationError(HTTPError):
    def __init__(self, message: str = "Validation Error"):
        super().__init__(422, message)

class NotFoundError(HTTPError):
    def __init__(self, message: str = "Not found"):
        super().__init__(404, message)

class ForbiddenError(HTTPError):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(403, message)