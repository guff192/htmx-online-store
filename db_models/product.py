from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base


class ProductDbModel(Base):
    __tablename__ = "products"

    _id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False, unique=True)

    description = Column(String(1000))
    price = Column(Integer, nullable=False)

    count = Column(Integer, nullable=False, default=0)
    newcomer = Column(Boolean, default=False, nullable=False)

    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    manufacturer = relationship("ManufacturerDbModel", back_populates="products")

    soldered_ram = Column(Integer, default=0, nullable=False)
    can_add_ram = Column(Boolean, default=True, nullable=False)
    resolution = Column(String(10), nullable=False)
    resolution_name = Column(String(12), nullable=False, default="")
    cpu = Column(String(12), nullable=False)
    gpu = Column(String(12), nullable=False)
    touch_screen = Column(Boolean, default=False, nullable=False)
    cpu_speed = Column(String(12), nullable=True)
    cpu_graphics = Column(String(32), nullable=True)

    available_configurations = relationship(
        "AvailableProductConfigurationDbModel",
        back_populates="product",
    )

    default_configuration_id = Column(Integer, ForeignKey("product_configurations.id"))
    default_configuration = relationship("ProductConfigurationDbModel")


class AvailableProductConfigurationDbModel(Base):
    __tablename__ = "available_product_configurations"

    id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    product = relationship("ProductDbModel", back_populates="available_configurations")

    configuration_id = Column(Integer, ForeignKey("product_configurations.id"))
    configuration = relationship("ProductConfigurationDbModel")
