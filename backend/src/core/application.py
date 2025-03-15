import logging
from contextlib import asynccontextmanager
from typing import Callable, Coroutine

from fastapi import FastAPI, APIRouter, Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.aws import init_bucket, get_aws_creator
from src.core.exc import HTTPError, HTTPErrorModel, HTTPValidationErrorModel


def create_app(
        routers: list[APIRouter],
        startup_tasks: list[Callable[[], Coroutine]] = None,
        shutdown_tasks: list[Callable[[], Coroutine]] = None,
        ignoring_log_endpoints: list[tuple[str, str]] = None,  # tuple[endpoint_path, method]
        root_path: str = "",
):

    startup_tasks = startup_tasks or []
    shutdown_tasks = shutdown_tasks or []
    ignoring_log_endpoints = ignoring_log_endpoints or []

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        for task in startup_tasks:
            await task()

        async with get_aws_creator() as aws_client:
            _app.extra['aws_client'] = aws_client
            await init_bucket(aws_client)
            yield

        for task in shutdown_tasks:
            await task()

    app = FastAPI(
        title="ZoomAD Platform",
        lifespan=lifespan,
        responses={
            422: {"model": HTTPValidationErrorModel},
        },
        root_path=root_path
    )

    for router in routers:
        app.include_router(router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        allow_credentials=True
    )
    app.add_middleware(
        ProxyHeadersMiddleware,
        trusted_hosts=["*"]
    )

    @app.exception_handler(RequestValidationError)
    async def exc_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(HTTPValidationErrorModel(
            code=422,
            message="Validation Error",
            detail=exc.errors()
        ).model_dump(), 422)

    Instrumentator(
        excluded_handlers=["/system/ping", "/metrics"]
    ).instrument(app).expose(app, include_in_schema=False)

    app.add_exception_handler(HTTPError, HTTPError.handler)

    logger = logging.getLogger("uvicorn.access")
    logger.addFilter(LoggingFilter(ignoring_log_endpoints, root_path))

    logging.basicConfig(
        format='[%(asctime)s.%(msecs)03dZ] %(name)s %(levelname)s %(message)s'
    )

    return app


class LoggingFilter(logging.Filter):
    def __init__(self, ignoring_log_endpoints: list[tuple[str, str]], root_path: str = "") -> None:
        super().__init__()
        self.ignoring_log_endpoints = ignoring_log_endpoints
        self.root_path = root_path

    def filter(self, record: logging.LogRecord) -> bool:
        for endpoint, method in self.ignoring_log_endpoints:
            if f"{method.upper()} {endpoint}" in record.getMessage().replace(self.root_path, "", 1):
                return False
        return True