from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import ForeignKey

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id")
    )

    address_id = Column(
        Integer,
        ForeignKey("addresses.id")
    )

    total_amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String,
        default="Pending"
    )