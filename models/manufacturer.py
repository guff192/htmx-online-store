from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.session import Base



class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column("id", Integer, primary_key=True,
                index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    products = relationship("Product", back_populates="manufacturer")


