from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.payment import Payment
from app.models.order import Order
from app.models.customer import Customer

from app.schemas.payment import PaymentCreate

from app.routers.auth import (
    get_current_customer
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/pay")
def make_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    order = (
        db.query(Order)
        .filter(
            Order.id == payment.order_id,
            Order.customer_id ==
            current_customer.id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    payment_record = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=payment.payment_method,
        payment_status="Paid"
    )

    db.add(payment_record)

    order.status = "Paid"

    db.commit()
    db.refresh(payment_record)

    return {
        "message": "Payment successful",
        "payment_id": payment_record.id
    }


@router.get("/")
def get_payments(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    orders = (
        db.query(Order)
        .filter(
            Order.customer_id ==
            current_customer.id
        )
        .all()
    )

    order_ids = [o.id for o in orders]

    payments = (
        db.query(Payment)
        .filter(
            Payment.order_id.in_(order_ids)
        )
        .all()
    )

    return payments