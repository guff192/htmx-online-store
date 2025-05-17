from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType, UUIDType

from db.session import Base
from db_models.order import OrderDbModel


class UserDbModel(Base):
    __tablename__ = 'users'

    id = Column('id', UUIDType(binary=False), primary_key=True, index=True)
    google_id = Column(String(21), unique=True)
    yandex_id = Column(Integer, unique=True)

    name = Column(String(255), nullable=False)
    email = Column(EmailType, unique=True)
    phone = Column(String(255), unique=True)

    profile_img_url = Column(String(255))

    is_admin = Column(Boolean, default=False, nullable=False)

    products = relationship('CartProductDbModel', back_populates='user')

    orders = relationship(OrderDbModel, back_populates='user')
