from typing import Any, NamedTuple


class CacheValueSchema(NamedTuple):
    value: Any
    expires_at: int


