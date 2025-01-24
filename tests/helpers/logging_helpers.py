from loguru import logger

from app.config import Settings
from dto.product_dto import ProductDTO
from models.product import Product


def log_product_short(product: Product | ProductDTO):
    if isinstance(product, ProductDTO):
        product_id = product.id
    elif hasattr(product, "_id"):
        product_id = product._id
    else:
        logger.error(f"Unknown product type: {type(product) = }\n\n{product = }")
        return
    short_product = {
        "python_id": id(product),
        "id": product_id,
        "name": product.name,
        "count": product.count,
        "price": product.price,
    }
    logger.debug(f"{short_product = }")


