from src.core.redis import redis_factory


__all__ = ("get_enabled_moderation", "update_enabled_moderation")


_MODERATION: bool | None = None


async def get_enabled_moderation() -> bool:
    global _MODERATION
    if _MODERATION is not None: return _MODERATION
    _MODERATION = bool.from_bytes(await redis_factory().get("backend:moderation") or b'\x00')
    return _MODERATION

async def update_enabled_moderation(enabled: bool) -> None:
    global _MODERATION
    _MODERATION = enabled
    await redis_factory().set("backend:moderation", enabled.to_bytes(1))