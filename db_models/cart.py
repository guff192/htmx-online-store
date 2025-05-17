from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

from db.session import Base


class CartProductDbModel(Base):
    __tablename__ = "cart_products"

    id = Column("id", Integer, primary_key=True, index=True)

    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"))
    user = relationship("UserDbModel", back_populates="products")

    product = relationship("ProductDbModel")
    product_id = Column(Integer, ForeignKey("products.id"))

    configurations = relationship(
        "CartProductConfigurationDbModel", back_populates="cart_product"
    )

    count = Column(Integer, nullable=False, default=1)


class CartProductConfigurationDbModel(Base):
    __tablename__ = "cart_product_configurations"

    id = Column("id", Integer, primary_key=True, index=True)

    cart_product_id = Column(Integer, ForeignKey("cart_products.id"))
    cart_product = relationship("CartProductDbModel", back_populates="configurations")

    configuration_id = Column(Integer, ForeignKey("product_configurations.id"))
    configuration = relationship("ProductConfigurationDbModel")
