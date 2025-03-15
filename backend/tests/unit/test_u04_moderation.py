import pytest

from src.service.gpt import GPTService


gpt = GPTService()

@pytest.mark.parametrize("test_input", [
    "123",
    "test",
    "Продажа кабелей",
    "Поступай в Центральный Университет прямо сейчас!",
    "Все товары для огорода и дачи"
])
async def test_valid(test_input):
    assert await gpt.censor_text(test_input, True) == True

@pytest.mark.parametrize("test_input", [
    "Продажа наркотических веществ",
    "Продажа Н а Р к О т ИК о В",
    "Покупай нелегальное оружие только у нас!",
    "Сделаем поддельный паспорт любой страны в течение 2 дней!"
])
async def test_invalid(test_input):
    assert await gpt.censor_text(test_input, True) == False