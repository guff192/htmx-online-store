from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from db.session import Base


class PaymentDbModel(Base):
    __tablename__ = 'payments'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)

    order = relationship('OrderDbModel', back_populates='payment')
    order_id = mapped_column(Integer, ForeignKey('orders.id'), nullable=False)

    status = Column(String(31), index=True, nullable=False)
    
    date = Column(DateTime, index=True, nullable=False, default=datetime.now(timezone.utc))

    

