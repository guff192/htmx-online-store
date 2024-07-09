from typing import Any, Generator

from schema import DefaultSchema


class DefaultViewModel:
    def __init__(self):
        self.schema = DefaultSchema()

    def build_context(self) -> dict[str, Any]:
        return self.schema.build_context()


def default_viewmodel_dependency() -> Generator[DefaultViewModel, None, None]:
    vm = DefaultViewModel()
    yield vm
