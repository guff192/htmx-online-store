from typing import Generator
from fastapi import Depends
from schema.banner_schema import BannerList
from services.banner_service import BannerService, banner_service_dependency


class BannerViewModel:
    def __init__(self, banner_service: BannerService) -> None:
        self._service = banner_service

    def get_all(self) -> BannerList:
        return BannerList(banners=self._service.get_all())


def banner_viewmodel_dependency(
    banner_service: BannerService = Depends(banner_service_dependency),
) -> Generator[BannerViewModel, None, None]:
    yield BannerViewModel(banner_service)

