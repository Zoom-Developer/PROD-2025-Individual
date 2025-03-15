from src.core.redis import redis_factory


__all__ = ("get_current_day", "update_day", "init_day")


_CURRENT_DAY: int | None = None


async def init_day():
    global _CURRENT_DAY
    _CURRENT_DAY = None
    await get_current_day()

async def get_current_day() -> int:
    global _CURRENT_DAY
    if _CURRENT_DAY is not None: return _CURRENT_DAY
    _CURRENT_DAY = int.from_bytes(await redis_factory().get("backend:day") or b'\x00')
    return _CURRENT_DAY

async def update_day(day: int) -> None:
    global _CURRENT_DAY
    _CURRENT_DAY = day
    await redis_factory().set("backend:day", day.to_bytes(8))