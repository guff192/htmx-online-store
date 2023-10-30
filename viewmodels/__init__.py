from typing import Any

from schema import DefaultSchema


class DefaultViewModel:
    def __init__(self):
        self.schema = DefaultSchema()

    def build_context(self) -> dict[str, Any]:
        return self.schema.build_context()

def default_viewmodel_dependency():
    vm = DefaultViewModel()
    yield vm
