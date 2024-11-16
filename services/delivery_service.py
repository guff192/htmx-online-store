from re import match
from time import time
from typing import Generator

from jose import jwt
import requests
from loguru import logger

from app.config import Settings
from schema.order_schema import CitySchema, OrderProductSchema, RegionSchema
from storage.cache_storage import MemoryCacheStorage


settings = Settings()
cache = MemoryCacheStorage()
MAIN_REGIONS = [
    'Москва', 'Санкт-Петербург',
    'Московская область', 'Ленинградская область',
]
MAIN_CITIES = [
    'Москва', 'Санкт-Петербург',
]
STANDARD_HEIGHT = 31
STANDARD_WIDTH = 8
STANDARD_LENGTH = 47
STANDARD_WEIGHT = 3000


class DeliveryService:
    def __init__(self):
        self.cdek_base_api_url = settings.cdek_base_api_url
        self._cdek_api_token: str = ''
        self._cdek_account: str = settings.cdek_account
        self._cdek_secure_password: str = settings.cdek_secure_password
        self.cdek_shop_city_id: int = settings.cdek_shop_city_id
    
    def _token_expired(self) -> bool:
        if not self._cdek_api_token:
            return True
        
        decoded_token = jwt.decode(
            self._cdek_api_token,
            key='',
            algorithms=['RS256'],
            options={'verify_signature': False}
        )
        if decoded_token['exp'] < int(time()):
            self._cdek_api_token = ''
            return True
        return False

    def _get_cdek_auth_token(self) -> str:
        if not self._token_expired():
            return self._cdek_api_token

        params = {
            'grant_type': 'client_credentials',
            'client_id': self._cdek_account,
            'client_secret': self._cdek_secure_password,
        }
        token_response = requests.post(f'{self.cdek_base_api_url}/oauth/token', params=params)
        token_response.raise_for_status()
        self._cdek_api_token = token_response.json()['access_token']

        return self._cdek_api_token

    @cache.cache_response
    def get_regions(self) -> list[RegionSchema]:
        auth_token = self._get_cdek_auth_token()
        headers = {'Authorization': f'Bearer {auth_token}'}
        params = {'size': 1000, 'country_codes': ['RU']}
        response = requests.get(
            f'{self.cdek_base_api_url}/location/regions', headers=headers, params=params
        )
        response.raise_for_status()
        regions_json = response.json()

        regions_list = [
            RegionSchema(code=region['region_code'], name=region['region'])
            for region in regions_json
        ]
        regions_list.sort(key=lambda region: region.name if region.name not in MAIN_REGIONS else '')

        return regions_list

    def get_cities(self, region_code: int) -> list[CitySchema]:
        auth_token = self._get_cdek_auth_token()

        headers = {'Authorization': f'Bearer {auth_token}'}
        params = {'size': 1000, 'region_code': region_code}
        response = requests.get(
            f'{self.cdek_base_api_url}/location/cities', headers=headers, params=params
        )
        response.raise_for_status()
        cities_json = response.json()

        cities_list = [
            CitySchema(code=city['code'], name=city['city'])
            for city in cities_json
        ]
        cities_list.sort(key=lambda city: city.name if city.name not in MAIN_CITIES else '')

        return cities_list

    def get_shipping_cost(
        self,
        receiver_city_id: int,
        products_count: int,
    ) -> int:
        auth_token = self._get_cdek_auth_token()

        packages = [
            {"weight": STANDARD_WEIGHT, "length": STANDARD_LENGTH, "width": STANDARD_WIDTH, "height": STANDARD_HEIGHT}
            for _ in range(products_count)
        ]

        headers = {"Authorization": f"Bearer {auth_token}"}
        body = {
            "from_location": {"code": self.cdek_shop_city_id},
            "to_location": {"code": receiver_city_id},
            "packages": packages,
            "type": 1,
            "tariff_code": 139
        }
        response = requests.post(
            f"{self.cdek_base_api_url}/calculator/tariff", headers=headers, json=body
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(response.json())
            raise e

        response = response.json()
        return int(response['total_sum'])

    def create_delivery_order(
        self,
        order_id: int,
        receiver_city_id: int,
        receiver_address: str,
        recipient_name: str,
        recipient_phone: str,
        recipient_email: str,
        products: list[OrderProductSchema] = [],
    ) -> str:
        auth_token = self._get_cdek_auth_token()
        recipient_name = f'Покупатель с номером {recipient_name}' if match(r'\d+', recipient_name) else recipient_name

        headers = {"Authorization": f"Bearer {auth_token}"}

        # Build the request body with provided information
        package_items = [product.to_package_item() for product in products]
        packages = {
            "number": f"order-{order_id}", "comment": "Упаковка",
            "height": 8, "length": 31, "width": 47, "weight": 3000,
            "items": package_items,
        }
        body = {
            "number": order_id,
            "type": 1,
            "comment": "Заказ с сайта",
            "delivery_recipient_cost": {"value": 0},
            "from_location": {
                "code": self.cdek_shop_city_id,
                "address": "Садовая-Кудринская ул., 23, стр. 5",
            },
            "to_location": {
                "code": receiver_city_id,
                "address": receiver_address,
            },
            "packages": packages,
            "recipient": {
                "name": recipient_name,
                "phones": [{"number": recipient_phone}],
                "email": recipient_email,
            },
            "tariff_code": 139,
        }

        response = requests.post(f"{self.cdek_base_api_url}/orders", headers=headers, json=body)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(response.json())
            raise e

        response = response.json()
        order_uuid = response['entity']['uuid']

        return order_uuid

    def get_cdek_order_number(self, order_id: int) -> str:
        auth_token = self._get_cdek_auth_token()

        headers = {"Authorization": f"Bearer {auth_token}"}

        response = requests.get(f"{self.cdek_base_api_url}/orders?im_number={order_id}", headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(response.json())
            raise e

        response = response.json()
        logger.debug(response)
        cdek_number = response['entity']['cdek_number']
        return cdek_number


def delivery_service_dependency() -> Generator[DeliveryService, None, None]:
    service = DeliveryService()
    yield service

