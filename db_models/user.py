from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy_utils import EmailType, UUIDType

from db.session import Base
from db_models.order import Order


class User(Base):
    __tablename__ = 'users'

    id = Column('id', UUIDType(binary=False), primary_key=True, index=True)
    google_id = Column(String(21), unique=True)
    yandex_id = Column(Integer, unique=True)

    name = Column(String(255), nullable=False)
    email = Column(EmailType, unique=True)
    phone = Column(String(255), unique=True)

    profile_img_url = Column(String(255))

    is_admin = Column(Boolean, default=False, nullable=False)

    products = relationship('UserProduct', back_populates='user')

    orders = relationship(Order, back_populates='user')


class UserProduct(Base):
    __tablename__ = 'user_products'

    id = Column('id', Integer, primary_key=True, index=True)

    user = relationship('User', back_populates='products')
    user_id = mapped_column(ForeignKey('users.id'))

    product = relationship('ProductDbModel', back_populates='users')
    product_id = mapped_column(ForeignKey('products.id'))

    selected_configuration = relationship(
        'ProductConfigurationDbModel',
    )
    selected_configuration_id = mapped_column(
        ForeignKey('product_configurations.id'), nullable=False
    )

    count = Column(Integer, nullable=False, default=1)

