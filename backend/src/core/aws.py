from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

import aioboto3
from aiobotocore.client import AioBaseClient
from botocore.exceptions import ClientError
from fastapi import Depends, Request

from src.config import config


# @asynccontextmanager
# async def get_aws_client() -> AsyncGenerator[AioBaseClient, None]:
#     session = aioboto3.Session()
#     async with session.client(
#         "s3",
#         endpoint_url=config.aws_url,
#         aws_access_key_id=config.aws_access_key_id,
#         aws_secret_access_key=config.aws_secret_access_key
#     ) as client:
#         yield client
#
# async def get_aws_client_di():
#     async with get_aws_client() as client:
#         yield client

def get_aws_creator():
    session = aioboto3.Session()
    return session.client(
        "s3",
        endpoint_url=config.aws_url,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key
    )

async def init_bucket(client: AioBaseClient):
    try:
        await client.create_bucket(Bucket=config.aws_images_bucket)
        print("Bucket created")
    except ClientError:
        pass

async def get_aws_client(request: Request):
    return request.app.extra['aws_client']

AWSClientDep = Annotated[AioBaseClient, Depends(get_aws_client)]