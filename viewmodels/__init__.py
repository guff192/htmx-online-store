from typing import Any, Generator

from schema import DefaultSchema
from schema.user_schema import LoggedUser


class DefaultViewModel:
    def __init__(self):
        self.schema = DefaultSchema()

    def build_context(self) -> dict[str, Any]:
        return self.schema.build_context()

    def build_context_with_user(self, user: LoggedUser) -> dict[str, Any]:
        context = self.build_context()
        context.update(user=user)
        return context


def default_viewmodel_dependency() -> Generator[DefaultViewModel, None, None]:
    vm = DefaultViewModel()
    yield vm
