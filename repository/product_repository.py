from typing import Generator
from fastapi import Depends
from loguru import logger
from sqlalchemy import Select, inspect, or_, select
from sqlalchemy.orm import Query, Session

from db.session import db_dependency, get_db
from dto.product_dto import ProductDTO
from models.product import AvailableProductConfiguration, Product, ProductConfiguration
from models.manufacturer import Manufacturer
from models.user import UserProduct
from repository.configuration_repository import (
    ConfigurationRepository,
    configuration_repository_dependency, get_configuration_repository
)


class ProductRepository:
    def __init__(
        self,
        db: Session,
        configuration_repository: ConfigurationRepository
    ):
        self.db = db
        self._configuration_repository = configuration_repository

    def _add_query_filter(self, stmt: Select[tuple[Product]], query: str | None) -> Select[tuple[Product]]:
        if not query:
            return stmt
        query_search_term = f'%{query.replace(" ", "%")}%'
        return stmt.where(or_(
            Product.name.ilike(query_search_term),
            Product.description.ilike(query_search_term)
        ))

    def _add_price_filter(self, stmt: Select[tuple[Product]], price_from: int, price_to: int) -> Select[tuple[Product]]:
        return stmt.where(Product.price.between(price_from, price_to))

    def _add_ram_filter(self, stmt: Select[tuple[Product]], ram: list[int]) -> Select[tuple[Product]]:
        if len(ram) == 0:
            return stmt
        compiled_initial_stmt = stmt.compile(compile_kwargs={"literal_binds": True}).string
        if "product_configurations" not in compiled_initial_stmt:
            stmt = (
                stmt
                .distinct()
                .join(AvailableProductConfiguration)
                .join(ProductConfiguration)
            )

        return stmt.where(ProductConfiguration.ram_amount.in_(ram))

    def _add_ssd_filter(self, stmt: Select[tuple[Product]], ssd: list[int]) -> Select[tuple[Product]]:
        if len(ssd) == 0:
            return stmt
        compiled_initial_stmt = stmt.compile(compile_kwargs={"literal_binds": True}).string
        if "product_configurations" not in compiled_initial_stmt:
            stmt = (
                stmt
                .distinct()
                .join(AvailableProductConfiguration)
                .join(ProductConfiguration)
            )

        return stmt.where(ProductConfiguration.ssd_amount.in_(ssd))

    def _add_cpu_filter(self, stmt: Select[tuple[Product]], cpu: list[str]) -> Select[tuple[Product]]:
        if not cpu:
            return stmt

        conditions = []
        for cpu_str in cpu:
            search_term = f'%{cpu_str}%'
            conditions.append(Product.cpu.ilike(search_term))

        if len(conditions) > 1:
            combined_condition = or_(*conditions)
        else:
            combined_condition = conditions[0]
        return stmt.where(combined_condition)

    def _add_resolution_filter(self, stmt: Select[tuple[Product]], resolution: list[str]) -> Select[tuple[Product]]:
        if len(resolution) == 0:
            return stmt
        return stmt.where(Product.resolution_name.in_(resolution))

    def _add_touchscreen_filter(self, stmt: Select[tuple[Product]], touchscreen: list[bool]) -> Select[tuple[Product]]:
        if len(touchscreen) == 0:
            return stmt
        return stmt.where(Product.touch_screen.in_(touchscreen))

    def _add_graphics_filter(self, stmt: Select[tuple[Product]], graphics: list[bool]) -> Select[tuple[Product]]:
        if len(graphics) == 0 or True in graphics and False in graphics:
            return stmt
        elif True in graphics:
            return stmt.where(Product.gpu != "")
        else:
            return stmt.where(Product.gpu == "") # noqa

    def get_all(
        self, query: str | None = None, offset: int = 0,
        price_from: int = 0, price_to: int = 150000,
        ram: list[int] = [], ssd: list[int] = [], cpu: list[str] = [],
        resolution: list[str] = [], touchscreen: list[bool] = [],
        graphics: list[bool] = []
    ) -> list[ProductDTO]:
        stmt = select(Product)
        stmt = self._add_query_filter(stmt, query)
        stmt = self._add_price_filter(stmt, price_from, price_to)
        stmt = self._add_ram_filter(stmt, ram)
        stmt = self._add_ssd_filter(stmt, ssd)
        stmt = self._add_cpu_filter(stmt, cpu)
        stmt = self._add_resolution_filter(stmt, resolution)
        stmt = self._add_touchscreen_filter(stmt, touchscreen)
        stmt = self._add_graphics_filter(stmt, graphics)
        stmt = stmt.offset(offset)
        stmt = stmt.limit(10)
        # logger.debug(stmt.compile(compile_kwargs={"literal_binds": True}))

        result = self.db.execute(stmt)
        model_products = result.scalars().all()

        # creating dto list
        dto_list: list[ProductDTO] = []
        for product_model in model_products:
            product_dict = product_model.__dict__

            product_id = product_dict.get('_id', 0)
            del product_dict['_id']
            product_dict['id'] = product_id
            product_dict['configurations'] = (
                self
                ._configuration_repository
                .get_configurations_for_product(product_id, ram, ssd)
            )
            product_dict['selected_configuration'] = None
            base_product_dto = ProductDTO(**product_dict)
            logger.debug(f'{product_dict = }')

            for selected_configuration in base_product_dto.configurations:
                if price_from <= base_product_dto.price + selected_configuration.additional_price <= price_to:
                    dto_copy = base_product_dto.model_copy(update={
                        'selected_configuration': selected_configuration
                    }, deep=True)
                    dto_list.append(dto_copy)

        # adding empty product to indicate that there are no more products
        if len(dto_list) == 0 and len(model_products) > 0:
            dto_list.append(ProductDTO(
                id=-5, name='', description='', price=0, count=0,
                manufacturer_id=0, configurations=[],
                selected_configuration=None, soldered_ram=0, can_add_ram=True,
                resolution='', cpu='', gpu='', touch_screen=False
            ))

        return dto_list

    def get_all_with_cart_info(
        self,
        query: str,
        user_id: str,
        offset: int,
        price_from: int = 0, price_to: int = 150000,
        ram: list[int] = [], ssd: list[int] = [], cpu: list[str] = [], 
        resolution: list[str] = [], touchscreen: list[bool] = [],
        graphics: list[bool] = [],
    ) -> list[ProductDTO]:
        result: list[ProductDTO] = []

        # Create query
        if query:
            stmt = (
                select(Product._id, Product.name, Product.description,
                       Product.price, Product.manufacturer_id,
                       Product.soldered_ram, Product.can_add_ram,
                       Product.resolution, Product.resolution_name, Product.cpu,
                       Product.gpu, Product.touch_screen,
                       UserProduct.count, UserProduct.selected_configuration_id).
                join(UserProduct,  # joining for getting count from user_product
                     Product._id == UserProduct.product_id,
                     isouter=True).
                where(or_(
                    Product.name.ilike(f'%{query.replace(" ", "%")}%'),
                    Product.description.ilike(f'%{query.replace(" ", "%")}%')
                )).
                where(  # filtering products in cart and products without user
                    or_(UserProduct.user_id == user_id,
                        UserProduct.user_id == None)).  # noqa: E711
                where(Product.count > 0).
                order_by(Product.name).
                slice(offset, offset + 10)
            )
        else:
            stmt = (
                select(Product._id, Product.name, Product.description,
                       Product.price, Product.manufacturer_id,
                       Product.soldered_ram, Product.can_add_ram,
                       Product.resolution, Product.resolution_name, Product.cpu,
                       Product.gpu, Product.touch_screen,
                       UserProduct.count, UserProduct.selected_configuration_id).
                join(UserProduct,  # joining for getting count from user_product
                     Product._id == UserProduct.product_id,
                     isouter=True).
                where(  # filtering products in cart and products without user
                    or_(UserProduct.user_id == user_id,
                        UserProduct.user_id == None)).  # noqa: E711
                where(Product.count > 0).
                slice(offset, offset + 10)
            )

        # Execute and add to result
        rows = self.db.execute(stmt).all()
        for row in rows:
            id_, product_name, product_description, product_price, \
            product_manufacturer_id, product_soldered_ram, product_can_add_ram, \
            product_resolution, product_resolution_name, product_cpu, product_gpu, \
            product_touch_screen, user_count, selected_configuration_id = row

            product_manufacturer_id = product_manufacturer_id if product_manufacturer_id else 0
            user_count = user_count if user_count else 0
            selected_configuration_id = selected_configuration_id if selected_configuration_id else 0

            configs = self._configuration_repository.get_configurations_for_product(id_)
            if not configs:
                continue

            # filtering by price
            if product_price < price_from or product_price > price_to:
                logger.debug(f'skipping product: {product_name} because of price filtering\n\n')
                continue

            # filtering by ram
            ram_filtered_configurations = tuple(filter(
                lambda c: c.ram_amount in ram, configs,
            ))
            if len(ram) > 0 and len(ram_filtered_configurations) == 0:
                logger.debug(f'skipping product: {product_name} because of ram filtering\n')
                continue

            # filtering by ssd
            ssd_filtered_configurations = list(filter(
                lambda c: c.ssd_amount in ssd, configs
            ))
            if len(ssd) > 0 and len(ssd_filtered_configurations) == 0:
                logger.debug(f'skipping product: {product_name} because of ssd filtering\n\n')
                continue

            # filtering by cpu
            if len(cpu) > 0 and not any(c.lower() in product_cpu.lower() for c in cpu):
                logger.debug(f'skipping product: {product_name} because of cpu filtering\n\n')
                continue
            
            # filtering by resolution
            if len(resolution) > 0 and not product_resolution_name in resolution:
                logger.debug(f'skipping product: {product_name} because of resolution filtering\n\n')
                continue

            # filtering by touchscreen
            if len(touchscreen) > 0 and product_touch_screen not in touchscreen:
                logger.debug(f'skipping product: {product_name} because of touchscreen filtering\n\n')
                continue

            # filtering by graphics
            if len(graphics) == 1:
                if True in graphics and not product_gpu:
                    logger.debug(f'skipping product: {product_name} because of graphics filtering\n\n')
                    continue
                if False in graphics and product_gpu:
                    logger.debug(f'skipping product: {product_name} because of graphics filtering\n\n')
                    continue

            filtered_configurations = tuple()
            if ram_filtered_configurations:
                if ssd_filtered_configurations:
                    filtered_configurations = tuple(filter(
                        lambda c: c in ssd_filtered_configurations,
                        ram_filtered_configurations
                    ))
                else:
                    filtered_configurations = ram_filtered_configurations
            elif ssd_filtered_configurations:
                filtered_configurations = ssd_filtered_configurations

            if filtered_configurations:
                for selected_configuration in filtered_configurations:
                    if price_from <= product_price + selected_configuration.additional_price <= price_to:
                        result.append(
                            ProductDTO(
                                id=id_, name=product_name, description=product_description,
                                price=product_price, count=user_count,
                                manufacturer_id=product_manufacturer_id,
                                soldered_ram=product_soldered_ram, can_add_ram=product_can_add_ram,
                                resolution=product_resolution, cpu=product_cpu, gpu=product_gpu,
                                touch_screen=product_touch_screen,
                                configurations=configs, selected_configuration=selected_configuration,
                            )
                        )
            else:
                result.append(
                    ProductDTO(
                       id=id_, name=product_name, description=product_description,
                       price=product_price, count=user_count,
                       manufacturer_id=product_manufacturer_id,
                       soldered_ram=product_soldered_ram, can_add_ram=product_can_add_ram,
                       resolution=product_resolution, cpu=product_cpu, gpu=product_gpu,
                       touch_screen=product_touch_screen,
                       configurations=configs, selected_configuration=None,
                    )
                )

        if len(result) == 0 and len(rows) > 0:
            result.append(ProductDTO(
                id=-5, name='', description='', price=0, count=0,
                manufacturer_id=0, configurations=[],
                selected_configuration=None, soldered_ram=0, can_add_ram=True,
                resolution='', cpu='', gpu='', touch_screen=False
            ))

        return result

    def get_newcomers(self, offset: int) -> list[Product]:
        product_list = (
            self.db.query(Product).
            filter(Product.newcomer == True).  # noqa: E712
            slice(offset, offset + 10).all()
        )

        return product_list

    def get_by_id(self, product_id) -> Product | None:
        return self.db.query(Product).get(product_id)

    def get_by_name(self, name: str) -> Product :
        return self.db.query(Product).filter(Product.name == name).first()

    def search(self, query: str, offset: int) -> list[Product]:
        return self.db.query(Product).\
            where(or_(
                Product.name.ilike(f'%{query.replace(" ", "%")}%'),
                Product.description.ilike(f'%{query.replace(" ", "%")}%')
            )).slice(offset, offset + 10).all()

    def create(self,
               name: str,
               description: str,
               price: int,
               count: int = 0,
               manufacturer: Manufacturer | None = None,
               configurations: list[ProductConfiguration] = [],
               soldered_ram: int = 0,
               can_add_ram: bool = True,
               resolution: str = '',
               resolution_name: str = '',
               cpu: str = '',
               gpu: str = '',
               touch_screen: bool = False,
               cpu_speed: str = '',
               cpu_graphics: str = '',
            ) -> Product:  # noqa: E125
        product = Product(
            name=name,
            description=description,
            price=price,
            count=count,
            manufacturer=manufacturer,
            soldered_ram=soldered_ram,
            can_add_ram=can_add_ram,
            resolution=resolution,
            resolution_name=resolution_name,
            cpu=cpu,
            gpu=gpu,
            touch_screen=touch_screen,
            cpu_speed=cpu_speed,
            cpu_graphics=cpu_graphics,
        )
        self.db.add(product)
        self.db.flush([product])

        configs: list[AvailableProductConfiguration] = []
        for config in configurations:
            available_configuration = AvailableProductConfiguration(
                product_id=product._id,
                configuration=config
            )
            self.db.add(available_configuration)
            configs.append(available_configuration)
        self.db.commit()
        self.db.flush(configs)

        product = self.get_by_id(product._id)
        return product

    def update(self,
               id: int,
               name: str,
               description: str,
               price: int,
               count: int,
               manufacturer: Manufacturer,
               configurations: list[ProductConfiguration],
               soldered_ram: int = 0,
               can_add_ram: bool = True,
               resolution: str = '',
               resolution_name: str = '',
               cpu: str = '',
               gpu: str = '',
               touch_screen: bool = False,
               cpu_speed: str = '',
               cpu_graphics: str = '') -> int:

        updated_product_query = self.db.query(Product).filter(
            Product._id == id
        )
        found_product = updated_product_query.first()
        if not found_product:
            return 0
        found_product_dict = found_product.__dict__
        logger.debug(f'Found product to update (in repo): {found_product_dict = }')

        updated_products_count = updated_product_query.update({
            Product.name: name,
            Product.description: description,
            Product.price: price,
            Product.count: count,
            Product.manufacturer_id: manufacturer.id,
            Product.soldered_ram: soldered_ram,
            Product.can_add_ram: can_add_ram,
            Product.resolution: resolution,
            Product.resolution_name: resolution_name,
            Product.cpu: cpu,
            Product.gpu: gpu,
            Product.touch_screen: touch_screen,
            Product.cpu_speed: cpu_speed,
            Product.cpu_graphics: cpu_graphics
        })
        self.db.commit()
        logger.debug('Updated product, flushing...')
        self.db.flush([found_product])
        found_product = updated_product_query.first()
        logger.debug(f'Updated product (in repo): {found_product.__dict__ = }')

        product_configs_query = self.db.query(AvailableProductConfiguration).\
            filter(AvailableProductConfiguration.product_id == id)
        found_configs = product_configs_query.all()
        found_config_ids = set(map(
            lambda found_config: found_config.__dict__.get('configuration_id'),
            found_configs
        ))
        update_config_ids = set(map(
            lambda available_config: available_config.id,
            configurations
        ))
        logger.debug(f'{found_config_ids = }\n{update_config_ids = }\n')
        new_available_configs = []
        if found_config_ids != update_config_ids:
            product_configs_query.delete()
            for config in configurations:
                available_configuration = AvailableProductConfiguration(
                    product=found_product, configuration=config
                )
                new_available_configs.append(available_configuration)
                self.db.add(available_configuration)
            
            self.db.commit()
            self.db.flush(new_available_configs)

        self.db.expire_all()

        return 1


def product_repository_dependency(
    db: Session = Depends(db_dependency),
    configuration_repo: ConfigurationRepository = Depends(
        configuration_repository_dependency
    )
) -> Generator[ProductRepository, None, None]:
    repo = ProductRepository(db, configuration_repo)
    yield repo


def get_product_repository(
    db: Session = get_db(),
    configuration_repo: ConfigurationRepository = get_configuration_repository()
) -> ProductRepository:
    return ProductRepository(db, configuration_repo)

