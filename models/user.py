from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy_utils import UUIDType

from db.session import Base


class User(Base):
    __tablename__ = 'users'

    id = Column('id', UUIDType(binary=False), primary_key=True, index=True)
    google_id = Column(String(21), unique=True)

    name = Column(String(255), nullable=False)

    profile_img_url = Column(String(255))

    is_admin = Column(Boolean, default=False, nullable=False)


class UserProduct(Base):
    __tablename__ = 'user_products'

    id = Column('id', Integer, primary_key=True, index=True)

    user_id = Column(
        UUIDType(binary=False),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey('products.id', ondelete='CASCADE'),
        nullable=False
    )

    count = Column(Integer, nullable=False, default=1)

