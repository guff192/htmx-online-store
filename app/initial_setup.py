from fastapi import HTTPException
from loguru import logger
import requests
from db.session import Session, db_dependency

from .config import Settings
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
    product_repository = ProductRepository(db)
    manufacturer_repository = ManufacturerRepository(db)
    product_service = ProductService(
        product_repository, S3ProductPhotoStorage(), manufacturer_repository
    )

    for product_data in data:
        logger.debug(product_data)
        name = product_data.get("name", "")
        description = product_data.get("description", "")
        price = product_data.get("price", 0)
        count = product_data.get("count", 0)
        manufacturer_name = product_data.get("manufacturer_name", "")
        if not name or not price or price == '#N/A':
            continue
        # Validate data using the schema
        product_create = ProductCreate(
            name=name,
            description=description,
            price=price,
            count=count if count != '#N/A' else 0,
            manufacturer_name=manufacturer_name
        )

        try:
            # Use the service to create the product
            product_service.create(product_create)
        except HTTPException as e:
            logger.info(f"Error creating product: {e.detail}")


if __name__ == "__main__":
    with next(db_dependency()) as db:
        fetch_products(db)

