from abc import ABC
from typing import Generator

import boto3
from loguru import logger
from mypy_boto3_s3.client import S3Client
from pydantic_core import Url

from app.config import Settings
from schema.product_schema import ProductPhotoPath, ProductPhotoSize
from storage.cache_storage import MemoryCacheStorage


settings = Settings()
cache = MemoryCacheStorage()


class ProductPhotoStorage(ABC):
    def __init__(self) -> None:
        raise NotImplementedError

    def get_url(
        self,
        product_path: ProductPhotoPath
    ) -> Url:
        raise NotImplementedError

    def get_main_photo_by_name(
            self,
            name: str,
            size: ProductPhotoSize = ProductPhotoSize.small
    ) -> ProductPhotoPath | None:
        raise NotImplementedError

    def get_all_by_name(
        self,
        name: str,
        size: ProductPhotoSize = ProductPhotoSize.thumbs
    ) -> list[ProductPhotoPath]:
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

        self._s3: S3Client = boto3.client(
            service_name='s3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=f'{access_key_id}',
            aws_secret_access_key=f'{access_key_secret}'
        )
        self._bucket_name = bucket_name
        self._public_bucket_url = public_bucket_url

    def get_url(
            self, product_path: ProductPhotoPath
    ) -> Url:
        return Url(f'{self._public_bucket_url}{product_path.full_path}')

    def get_main_photo_by_name(
            self,
            name: str,
            size: ProductPhotoSize = ProductPhotoSize.small
    ) -> ProductPhotoPath | None:
        paths = self.get_all_by_name(name=name, size=size)
        if not paths:
            return None
        return paths[0]

    @cache.cache_response
    def get_all_by_name(
        self,
        name: str,
        size: ProductPhotoSize = ProductPhotoSize.thumbs
    ) -> list[ProductPhotoPath]:
        prefix = f'{name}/{size.value}' if size.value else f'{name}'
        response = self._s3.list_objects_v2(
            Bucket=self._bucket_name,
            Prefix=prefix,
            OptionalObjectAttributes=[
                'RestoreStatus',
            ]
        )
        response_contents = response.get('Contents')
        if not response_contents:
            return []

        objects = map(
            lambda obj: obj.get('Key', None),
            response_contents
        )
        product_photo_paths: list[ProductPhotoPath] = [
            ProductPhotoPath(file_name=obj.split('/')[-1], path=prefix)
            for obj in objects
            if obj is not None and '.' in obj
        ]

        return product_photo_paths


def product_photo_storage_dependency() -> Generator[ProductPhotoStorage, None, None]:
    yield S3ProductPhotoStorage()

