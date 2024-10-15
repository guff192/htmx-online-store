from time import time
from typing import Any, Callable

from loguru import logger

from schema.cache_schema import CacheValueSchema


class MemoryCacheStorage:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            logger.info('Creating memory cache storage')
            cls.instance = super(MemoryCacheStorage, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._response_cache: dict[tuple[str, tuple], Any] = {}
        self._values_cache: dict[str, CacheValueSchema] = {}

    def remove_expired_values(self) -> None:
        self._values_cache = {k: v for k, v in self._values_cache.items() if time() < v.expires_at}

    def cache_response(self, request_func: Callable[..., Any]):
        full_func_name = request_func.__qualname__

        def wrapper(*args, **kwargs) -> Any:
            if len(args) and hasattr(args[0], '__class__'):
                key_args = args[1:] + tuple(kwargs.items())
            else:
                key_args = args[:] + tuple(kwargs.items())

            if not (response := self._response_cache.get((full_func_name, key_args))):
                response = request_func(*args, **kwargs)
                self._response_cache[full_func_name, key_args] = response

            return response

        return wrapper

    def add_value_to_cache(self, key: str, value: Any, expires_at: int = 0) -> None:
        self._values_cache[key] = CacheValueSchema(value=value, expires_at=expires_at)

    def get_cached_value(self, key: str) -> Any:
        cached_value = self._values_cache.get(key)
        if not cached_value:
            return None

        if cached_value.expires_at and time() >= cached_value.expires_at:
            del self._values_cache[key]
            return None
        return cached_value.value



