from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base


class Product(Base):
    __tablename__ = 'products'

    _id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False, unique=True)

    description = Column(String(1000))
    price = Column(Integer)

    count = Column(Integer, default=0)
    newcomer = Column(Boolean, default=False, nullable=False)

    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'))
    manufacturer = relationship('Manufacturer', back_populates='products')

    users = relationship('UserProduct', back_populates='product')


class Manufacturer(Base):
    __tablename__ = 'manufacturers'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    products = relationship('Product', back_populates='manufacturer')

