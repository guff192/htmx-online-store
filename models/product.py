from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.session import Base


class Product(Base):
    __tablename__ = 'products'

    _id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False, unique=True)

    description = Column(String(1000))
    price = Column(Integer)

    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'))
    manufacturer = relationship('Manufacturer')


class Manufacturer(Base):
    __tablename__ = 'manufacturers'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    # products = relationship('Product', back_populates='manufacturer')



