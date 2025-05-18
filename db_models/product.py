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
