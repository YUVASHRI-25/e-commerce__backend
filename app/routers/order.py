from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart import CartItem
from app.models.product import Product
from app.models.address import Address
from app.models.customer import Customer

from app.schemas.order import OrderCreate

from app.routers.auth import (
    get_current_customer
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/place")
def place_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    address = (
        db.query(Address)
        .filter(
            Address.id == order.address_id,
            Address.customer_id ==
            current_customer.id
        )
        .first()
    )

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    cart_items = (
        db.query(CartItem)
        .filter(
            CartItem.customer_id ==
            current_customer.id
        )
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = 0

    for item in cart_items:

        product = (
            db.query(Product)
            .filter(
                Product.id ==
                item.product_id
            )
            .first()
        )

        if item.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}"
            )

        total_amount += (
            product.price *
            item.quantity
        )

    new_order = Order(
        customer_id=current_customer.id,
        address_id=order.address_id,
        total_amount=total_amount,
        status="Pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in cart_items:

        product = (
            db.query(Product)
            .filter(
                Product.id ==
                item.product_id
            )
            .first()
        )

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(order_item)

        product.stock -= item.quantity

    (
        db.query(CartItem)
        .filter(
            CartItem.customer_id ==
            current_customer.id
        )
        .delete()
    )

    db.commit()

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "total_amount": total_amount
    }


@router.get("/")
def get_orders(
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

    return orders


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
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

    items = (
        db.query(OrderItem)
        .filter(
            OrderItem.order_id ==
            order.id
        )
        .all()
    )

    return {
        "order": order,
        "items": items
    }

@router.put("/status/{order_id}")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_statuses = [
        "Pending",
        "Paid",
        "Shipped",
        "Out For Delivery",
        "Delivered",
        "Cancelled"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    order.status = status

    db.commit()

    return {
        "message": "Order status updated",
        "status": status
    }

