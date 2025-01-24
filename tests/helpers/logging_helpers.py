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


def log_test_info(info: str, level: int = 3):
    str_lengths = {0: 100, 1: 80, 2: 65, 3: 50}
    eq_str = "=" * str_lengths[level]
    if level == 0:
        info_str = f"{info : ^100}"
    elif level == 1:
        info_str = f"{info : ^80}"
    elif level == 2:
        info_str = f"{info : ^65}"
    else:
        info_str = f"{info : ^50}"

    logger.info(
        "\n" * 2
        + eq_str
        + "\n"
        + info_str
        + "\n"
        + eq_str
    )
