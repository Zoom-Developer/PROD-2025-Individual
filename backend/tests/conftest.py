import asyncio
import uuid

import aioboto3
import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from src.config import config
from src.core.db.engine import get_engine
from src.core.utils import get_current_day, update_day, update_enabled_moderation
from src.main import app
from src.repo.advertiser import AdvertiserRepository
from src.repo.campaign import CampaignRepository
from src.repo.client import ClientRepository
from src.service.advertiser import AdvertiserService
from src.service.campaign import CampaignService
from src.service.client import ClientService
from src.service.files import FilesService
from src.service.gpt import GPTService


# FIXTURES

@pytest.fixture(scope="session")
def db_container():
    container = PostgresContainer(image="postgres:alpine")
    yield container.start()
    container.stop()

@pytest.fixture(scope="session")
def minio_container():
    container = MinioContainer(image="minio/minio")
    yield container.start()
    container.stop()

@pytest.fixture(scope="session")
def redis_container():
    container = RedisContainer(image="redis:alpine")
    yield container.start()
    container.stop()

@pytest.fixture(scope="function")
async def db_engine(db_container):
    postgres_conn_str = db_container.get_connection_url().replace('postgresql+psycopg2', 'postgresql+asyncpg')
    engine = create_async_engine(postgres_conn_str)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(db_engine):
    async with AsyncSession(db_engine) as session:
        yield session

@pytest.fixture(scope="function")
async def redis_config(redis_container):
    config.redis_host = redis_container.get_container_host_ip()
    config.redis_port = redis_container.get_exposed_port(redis_container.port)

    yield

    await update_day(0)
    await update_enabled_moderation(False)

@pytest.fixture(scope="function")
async def s3_session(minio_container):
    session = aioboto3.Session()
    minio_config = minio_container.get_config()
    async with session.client(
        "s3",
        endpoint_url="http://" + minio_config['endpoint'],
        aws_access_key_id=minio_config['access_key'],
        aws_secret_access_key=minio_config['secret_key']
    ) as conn:
        yield conn

@pytest.fixture(scope="function")
async def test_client(db_engine, minio_container, redis_config):
    app.dependency_overrides[get_engine] = lambda: db_engine

    minio_config = minio_container.get_config()
    config.aws_url = "http://" + minio_config['endpoint']
    config.aws_access_key_id = minio_config['access_key']
    config.aws_secret_access_key = minio_config['secret_key']

    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
        ) as c:
            yield c

@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# Service Fixtures

@pytest.fixture(scope="function")
def client_repo(db_session):
    return ClientRepository(db_session)

@pytest.fixture(scope="function")
def client_service(client_repo):
    return ClientService(client_repo)

@pytest.fixture(scope="function")
def advertiser_repo(db_session):
    return AdvertiserRepository(db_session)

@pytest.fixture(scope="function")
def advertiser_service(advertiser_repo, client_repo):
    return AdvertiserService(advertiser_repo, client_repo)

@pytest.fixture(scope="function")
def campaign_repo(db_session):
    return CampaignRepository(db_session)

@pytest.fixture(scope="function")
def campaign_service(campaign_repo, advertiser_repo, s3_session, redis_config):
    return CampaignService(campaign_repo, GPTService(), FilesService(s3_session))

# OTHER

async def create_client(cl: AsyncClient) -> str:
    client_id = str(uuid.uuid4())
    client = {
        "client_id": client_id,
        "login": "testuser",
        "age": 23,
        "location": "Moscow",
        "gender": "MALE"
    }
    response = await cl.post('/clients/bulk', json=[client])
    assert response.status_code == 201
    return client_id

async def create_advertiser(cl: AsyncClient) -> str:
    advertiser_id = str(uuid.uuid4())
    advertiser = {
        "advertiser_id": advertiser_id,
        "name": "Test Corp"
    }
    response = await cl.post('/advertisers/bulk', json=[advertiser])
    assert response.status_code == 201
    return advertiser_id

async def create_campaign(cl: AsyncClient, advertiser_id: str = None, date: int = 15) -> dict:
    advertiser_id = advertiser_id or await create_advertiser(cl)

    campaign = {
        "impressions_limit": 1000,
        "clicks_limit": 100,
        "cost_per_impression": 10,
        "cost_per_click": 100,
        "ad_title": "Test Title",
        "ad_text": "Test Test!",
        "start_date": date,
        "end_date": 30,
        "targeting": {}
    }

    # Базовое добавление
    response = await cl.post(f'/advertisers/{advertiser_id}/campaigns', json=campaign)
    assert response.status_code == 201
    return response.json()