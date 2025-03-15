from aiohttp import FormData

from .core import request
from exc import APIError


async def upload_file(file: bytes) -> tuple[str, str] | None:
    form = FormData()
    form.add_field("file", file)
    try:
        data = await request(
        f"/files",
            "POST",
            data=form,
        )
        return data['file_id'], data['image_url']
    except APIError:
        return None