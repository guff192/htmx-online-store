from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy_utils import UUIDType
from db.session import Base
from db_models.payment import Payment


class Order(Base):
    __tablename__ = 'orders'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)

    user = relationship('User', back_populates='orders')
    user_id = mapped_column(ForeignKey('users.id'), UUIDType())

    products = relationship('OrderProduct', cascade='all, delete')

    date = Column(DateTime, nullable=False)

    comment = Column('comment', String(255), nullable=False, default='')

    buyer_name = Column('buyer_name', String(255), nullable=False, default='')
    buyer_phone = Column('buyer_phone', String(255), nullable=False, default='')

    region_id = Column('region_id', Integer)
    region_name = Column('region_name', String(255), default='')

    city_id = Column('city_id', Integer)
    city_name = Column('city_name', String(255), default='')
    delivery_address = Column('delivery_address', String(255), nullable=False, default='')

    delivery_track_number = Column('delivery_track_number', String(255), default='')

    payment = relationship(Payment, back_populates='order', uselist=False)


class OrderProduct(Base):
    __tablename__ = 'order_products'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)

    order = relationship('Order', back_populates='products')
    order_id = mapped_column(ForeignKey('orders.id'))

    product = relationship('ProductDbModel')
    product_id = mapped_column(ForeignKey('products.id'))

    selected_configuration = relationship(
        'ProductConfigurationDbModel'
    )
    selected_configuration_id = mapped_column(
        ForeignKey('product_configurations.id'), nullable=False
    )

    count = Column(Integer, nullable=False, default=1)


