from fastapi import Depends
from repository.banner_repository import (
    BannerRepository, banner_repository_dependency
)
from schema.banner_schema import Banner as BannerSchema


class BannerService:
    def __init__(self, repo: BannerRepository) -> None:
        self._repo = repo

    def get_all(self) -> list[BannerSchema]:
        orm_banners = self._repo.get_all()

        banners: list[BannerSchema] = []
        for orm_banner in orm_banners:
            orm_banner_dict = orm_banner.__dict__
            banner_schema = BannerSchema(
                name=orm_banner_dict.get('name', ''),
                description=orm_banner_dict.get('description', ''),
                img_url=orm_banner_dict.get('img_url', ''),
            )
            banners.append(banner_schema)

        return banners


def banner_service_dependency(
    repo: BannerRepository = Depends(banner_repository_dependency),
) -> BannerService:
    service = BannerService(repo)
    return service

