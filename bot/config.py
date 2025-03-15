from dotenv import load_dotenv
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    api_url: str

    redis_host: str
    redis_port: int

load_dotenv()
config = Settings()