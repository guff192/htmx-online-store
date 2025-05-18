from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from db.session import Base


class ConfigurationTypeDbModel(Base):
    __tablename__ = "configuration_types"

    id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)

    name = Column(String(255), nullable=False, unique=True)

    img_url = Column(String(255), nullable=True)

    configurations = relationship(
        "ProductConfigurationDbModel", back_populates="configuration_type"
    )


class ProductConfigurationDbModel(Base):
    __tablename__ = "product_configurations"

    id = Column("id", Integer, primary_key=True, index=True, autoincrement=True)
    additional_price = Column(Integer, nullable=False, default=0)
    short_name = Column(String(255), nullable=True)

    configuration_type_id = Column(Integer, ForeignKey("configuration_types.id"))
    configuration_type = relationship(
        "ConfigurationTypeDbModel", back_populates="configurations"
    )

    value = Column(String(255), nullable=False, index=True)
