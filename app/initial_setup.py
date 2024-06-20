from fastapi import HTTPException
from loguru import logger
import requests
from sqlalchemy.orm import Session
from repository.configuration_repository import ConfigurationRepository

from .config import Settings
from db.session import db_dependency
from repository.manufacturer_repository import ManufacturerRepository
from repository.product_repository import ProductRepository
from schema.product_schema import ProductCreate
from services.product_service import ProductService
from storage.photo_storage import S3ProductPhotoStorage


settings = Settings()


def fetch_products(db: Session):
    # Fetch data from Google Spreadsheet via REST API
    logger.info("Fetching data from Google Spreadsheet...")
    response = requests.get(settings.posting_endpoint)
    data = response.json()

    # Initialize the service and repository
    product_repository = ProductRepository(db, ConfigurationRepository(db))
    manufacturer_repository = ManufacturerRepository(db)
    configuration_repository = ConfigurationRepository(db)
    product_service = ProductService(
        product_repository, S3ProductPhotoStorage(), manufacturer_repository,
        configuration_repository
    )

    basic_configs = product_service.get_all_basic_configs()

    for product_data in data:
        name = product_data.get("name", "")
        description = product_data.get("description", "")
        price = product_data.get("price", 0)
        count = product_data.get("count", 0)
        manufacturer_name = product_data.get("manufacturer_name", "")
        use_basic_configs = product_data.get("basic_configs", False)
        if not name or not price or price == '#N/A' or not use_basic_configs:
            logger.info(f"Skipping product: {product_data}")
            continue

        # Validate data using the schema
        product_create = ProductCreate(
            name=name,
            description=description,
            price=price,
            count=count if count != '#N/A' else 0,
            manufacturer_name=manufacturer_name,
            configurations=basic_configs,
        )

        try:
            # Use the service to create the product
            product = product_service.create(product_create)
            logger.info(f"Created product: {product}")
        except HTTPException as e:
            logger.info(f"Error creating product: {e.detail}")


if __name__ == "__main__":
    with next(db_dependency()) as db:
        fetch_products(db)

