from typing import Generator, Literal

import boto3
from loguru import logger
from mypy_boto3_s3.client import S3Client
from pydantic_core import Url

from app.config import Settings
from schema.product_schema import ProductPhotoPath


settings = Settings()


class ProductPhotoStorage:
    def __init__(self) -> None:
        raise NotImplementedError

    def get_url(self, product_path: ProductPhotoPath, small: bool = False) -> Url:
        raise NotImplementedError

    def get_main_photo_by_name(
            self,
            name: str,
            size: Literal['', 'small', 'thumbs'] = 'small'
    ) -> ProductPhotoPath | None:
        raise NotImplementedError

    def get_all_by_name(
        self,
        name: str,
        size: Literal['', 'small', 'thumbs'] = ''
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

    def get_url(self, product_path: ProductPhotoPath, small: bool = False) -> Url:
        return Url(f'{self._public_bucket_url}{product_path.full_path}')

    def get_main_photo_by_name(
            self,
            name: str,
            size: Literal['', 'small', 'thumbs'] = 'small'
    ) -> ProductPhotoPath | None:
        paths = self.get_all_by_name(name=name, size=size)
        if not paths:
            return None
        logger.debug(f'{paths[0]=}')
        return paths[0]

    def get_all_by_name(
        self,
        name: str,
        size: Literal['', 'small', 'thumbs'] = ''
    ) -> list[ProductPhotoPath]:
        prefix = f'{name}/{size}' if size else f'{name}'
        response = self._s3.list_objects_v2(
            Bucket=self._bucket_name,
            Prefix=prefix,
            OptionalObjectAttributes=[
                'RestoreStatus',
            ]
        )
        if not response.get('Contents'):
            return []

        products = list(filter(
            lambda product: product.get('Key', None),
            response.get('Contents')
        ))
        product_photo_paths: list[ProductPhotoPath] = [
            ProductPhotoPath(file_name=product.get('Key').split('/')[-1], path=prefix)
            for product in products
            if '.' in product.get('Key', '')
        ]

        return product_photo_paths


def product_photo_storage_dependency() -> Generator[ProductPhotoStorage, None, None]:
    yield S3ProductPhotoStorage()

