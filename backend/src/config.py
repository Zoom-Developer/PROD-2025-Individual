from dotenv import load_dotenv
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    database_host: str = "localhost"
    database_port: int = 5732
    database_user: str = ""
    database_password: str = ""
    database_name: str = ""

    openai_api_key: str = ""
    proxy_url: str = ""

    redis_host: str = "localhost"
    redis_port: int = 6379

    aws_url: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_images_bucket: str = "images"

    api_url: str = "http://localhost:8000"

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

load_dotenv()
config = Settings()