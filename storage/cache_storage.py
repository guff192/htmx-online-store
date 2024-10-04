from typing import Any, Callable

from loguru import logger


class MemoryCacheStorage:
    def __new__(cls):
        logger.debug('Creating response cache storage')
        if not hasattr(cls, 'instance'):
            cls.instance = super(MemoryCacheStorage, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self._cache: dict[tuple[str, tuple], Any] = {}

    def cache_response(self, request_func: Callable[..., Any]):
        full_func_name = request_func.__qualname__

        def wrapper(*args, **kwargs) -> Any:
            if len(args) and hasattr(args[0], '__class__'):
                key_args = args[1:] + tuple(kwargs.items())
            else:
                key_args = args[:] + tuple(kwargs.items())

            if not (response := self._cache.get((full_func_name, key_args))):
                response = request_func(*args, **kwargs)
                self._cache[full_func_name, key_args] = response

            logger.debug(f'self._cache[{full_func_name}, {key_args}]')
            return response

        return wrapper

