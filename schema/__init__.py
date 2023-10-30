from typing import Any, Callable
from fastapi import Request

from pydantic import BaseModel

from app.config import Settings


class Shop(BaseModel):
    name: str


class SchemaUtils:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SchemaUtils, cls).__new__(cls)
        return cls.instance
        
    def __init__(self):
        settings = Settings()
        self.shop: Shop = Shop(name=settings.shop_name)

    def add_shop_to_context(self, func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        def wrapper(*args, **kwargs):
            context = func(*args, **kwargs)
            context['shop'] = self.shop
            return context
        return wrapper


utils = SchemaUtils()


class DefaultSchema(BaseModel):
    @utils.add_shop_to_context
    def build_context(self) -> dict[str, Any]:
        return {}

