from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey

from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id")
    )

    full_name = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        nullable=False
    )

    address_line = Column(
        String,
        nullable=False
    )

    city = Column(
        String,
        nullable=False
    )

    state = Column(
        String,
        nullable=False
    )

    pincode = Column(
        String,
        nullable=False
    )

    country = Column(
        String,
        nullable=False
    )

    is_default = Column(
        Boolean,
        default=False
    )