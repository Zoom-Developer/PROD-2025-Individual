from contextvars import ContextVar
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine
)
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import config

__all__ = ("ping_db", "SessionDep", "get_session", "CTX_SESSION_DONT_CLOSE")

from src.core.exc import HTTPError

engine: AsyncEngine = create_async_engine(config.database_url, pool_size = 500, max_overflow = 100, pool_recycle=10)

# Зависимость для движка необходима для подмены в тестах
def get_engine() -> AsyncEngine:
    return engine

async def get_session(eng: AsyncEngine = Depends(get_engine)):
    session = AsyncSession(eng, expire_on_commit=False, autoflush=False)
    CTX_SESSION_DONT_CLOSE.set(False)
    try:
        yield session
        await session.commit()
    except HTTPError as err:
        if err.commit_db:
            await session.commit()
        raise err
    finally:
        if CTX_SESSION_DONT_CLOSE.get():
            # Необходимо для фоновых процессов
            return
        await session.close()

async def ping_db(session: AsyncSession) -> None:
    await session.exec(select(True))

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CTX_SESSION_DONT_CLOSE: ContextVar[bool] = ContextVar("CTX_SESSION_DONT_CLOSE", default=False)