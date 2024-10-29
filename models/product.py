from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base


class AvailableProductConfiguration(Base):
    __tablename__ = "available_product_configurations"

    id = Column("id", Integer, primary_key=True,
                index=True, autoincrement=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="configurations")

    configuration_id = Column(Integer, ForeignKey("product_configurations.id"))
    configuration = relationship(
        "ProductConfiguration", back_populates="products")


class ProductConfiguration(Base):
    __tablename__ = "product_configurations"

    id = Column("id", Integer, primary_key=True,
                index=True, autoincrement=True)
    ram_amount = Column(Integer, nullable=False, default=0)
    ssd_amount = Column(Integer, nullable=False, default=0)

    additional_price = Column(Integer, nullable=False, default=0)

    is_default = Column(Boolean, default=False, nullable=False)
    additional_ram = Column(Boolean, default=False, nullable=False)
    soldered_ram = Column(Integer, default=0, nullable=False)

    products = relationship(
        "AvailableProductConfiguration", back_populates="configuration"
    )


class Product(Base):
    __tablename__ = "products"

    _id = Column("id", Integer, primary_key=True,
                 index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False, unique=True)

    description = Column(String(1000))
    price = Column(Integer)

    count = Column(Integer, default=0)
    newcomer = Column(Boolean, default=False, nullable=False)

    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    manufacturer = relationship("Manufacturer", back_populates="products")

    soldered_ram = Column(Integer, default=0, nullable=False)
    can_add_ram = Column(Boolean, default=True, nullable=False)
    resolution = Column(String(10), nullable=False)
    cpu = Column(String(12), nullable=False)
    gpu = Column(String(12), nullable=False)
    touch_screen = Column(Boolean, default=False, nullable=False)

    users = relationship("UserProduct", back_populates="product")

    configurations = relationship(
        "AvailableProductConfiguration",
        back_populates="product",
    )

    default_configuration_id = Column(
        Integer, ForeignKey("product_configurations.id"))
    default_configuration = relationship("ProductConfiguration")

