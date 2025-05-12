from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.session import Base



class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column("id", Integer, primary_key=True,
                index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    logo_url = Column(String(255), nullable=True)

    products = relationship("ProductDbModel", back_populates="manufacturer")


