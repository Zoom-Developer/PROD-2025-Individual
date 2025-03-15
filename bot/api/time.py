from .core import request


async def set_day(day: int) -> None:
    await request("/time/advance", "POST", json={"current_date": day})

async def get_current_day() -> int:
    data = await request("/time", "GET")
    return data['current_date']