from sqlalchemy import Column, Integer, String
from db.session import Base


class Banner(Base):
    __tablename__ = 'banners'

    _id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False, unique=True)
    description = Column(String(1000))
    img_url = Column(String(255))

