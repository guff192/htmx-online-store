from typing import Any, Callable

from loguru import logger


class MemoryCacheStorage:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            logger.info('Creating memory cache storage')
            cls.instance = super(MemoryCacheStorage, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._response_cache: dict[tuple[str, tuple], Any] = {}
        self._values_cache: dict[str, Any] = {}

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

    def cache_value(self, key: str, value: Any):
        self._values_cache[key] = value

    def get_cached_value(self, key: str) -> Any:
        return self._values_cache.get(key)


