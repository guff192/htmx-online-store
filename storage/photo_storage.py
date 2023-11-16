from collections.abc import Mapping
from typing import Generator

import boto3
from loguru import logger
from pydantic_core import Url
from app.config import Settings

from schema.product_schema import ProductPhotoPath


settings = Settings()


class ProductPhotoStorage:
    def __init__(self) -> None:
        raise NotImplementedError

    def get_one(self, product_path: ProductPhotoPath) -> Url:
        raise NotImplementedError

    def get_main_photo_by_name(self, name: str) -> Url:
        raise NotImplementedError

    def get_all_by_name(self, name: str) -> list[Url]:
        raise NotImplementedError


class S3ProductPhotoStorage(ProductPhotoStorage):
    def __init__(self) -> None:
        public_bucket_url = settings.public_bucket_url
        bucket_name = settings.bucket_name
        account_id = settings.cloudflare_account_id
        access_key_id = settings.aws_access_key_id
        access_key_secret = settings.aws_secret_access_key
        # if any(map(bool, (account_id, access_key_id, access_key_secret, bucket_name))):
        #     # TODO: Change this to custom exception
        #     raise ValueError('Missing S3 credentials')

        self._s3 = boto3.client(
            service_name='s3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=f'{access_key_id}',
            aws_secret_access_key=f'{access_key_secret}'
        )
        self._bucket_name = bucket_name
        self._public_bucket_url = public_bucket_url

        for url in self.get_all_by_name(name='Apple MacBook Pro 16, M1 Pro 10c, 3456x2234, Retina'):
            logger.debug(str(url))

    def get_one(self, product_path: ProductPhotoPath) -> Url:
        return Url(f'{self._public_bucket_url}{product_path.full_path}')

    def get_main_photo_by_name(self, name: str) -> Url | None:
        urls = self.get_all_by_name(name=name)
        if not urls:
            return None
        return urls[0]

    def get_all_by_name(self, name: str) -> list[Url]:
        response = self._s3.list_objects_v2(
            Bucket=self._bucket_name,
            Prefix=f'{name}/',
            OptionalObjectAttributes=[
                'RestoreStatus',
            ]
        )
        if not response.get('Contents'):
            return []

        product_photo_paths: list[ProductPhotoPath] = [
            ProductPhotoPath(file_name=product['Key'].split('/')[-1], path=name)
            for product in response['Contents']
        ]

        return [self.get_one(product_path) for product_path in product_photo_paths]


def product_photo_storage_dependency() -> Generator[ProductPhotoStorage, None, None]:
    yield S3ProductPhotoStorage()

