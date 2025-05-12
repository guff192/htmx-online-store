from loguru import logger

from app.config import Settings
from dto.product_dto import ProductDTO
from db_models.product import ProductDbModel


def log_product_short(product: ProductDbModel | ProductDTO):
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
    str_lengths = {0: 115, 1: 100, 2: 85, 3: 70}
    eq_str = "=" * str_lengths[level]

    if level == 0:
        info_str = f"{info : ^115}"
    elif level == 1:
        info_str = f"{info : ^100}"
    elif level == 2:
        info_str = f"{info : ^85}"
    else:
        info_str = f"{info : ^70}"

    top_margin = 2 if level != 0 else 5
    logger.info(
        "\n" * top_margin
        + eq_str
        + "\n"
        + info_str
        + "\n"
        + eq_str
    )
