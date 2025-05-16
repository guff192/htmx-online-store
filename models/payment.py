from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class PaymentStatus(str, Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Payment(BaseModel):
    id: int
    order_id: int

    status: PaymentStatus
    date: datetime
