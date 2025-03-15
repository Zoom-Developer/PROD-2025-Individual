from typing import Callable, Coroutine, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import CTX_SESSION_DONT_CLOSE


__all__ = ("bg_db_task",)


async def bg_db_task(coro: Callable[[Any], Coroutine], session: AsyncSession, args: tuple = tuple()) -> None:
    CTX_SESSION_DONT_CLOSE.set(True)
    try:
        await coro(*args)
        await session.commit()
    except:
        pass
    finally:
        await session.close()