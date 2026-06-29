from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.cart import CartItem
from app.models.product import Product
from app.models.customer import Customer

from app.schemas.cart import (
    CartCreate,
    CartUpdate,
    CartResponse
)

from app.routers.auth import (
    get_current_customer
)

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.post("/add")
def add_to_cart(
    cart: CartCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    product = (
        db.query(Product)
        .filter(
            Product.id == cart.product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if cart.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    existing_item = (
        db.query(CartItem)
        .filter(
            CartItem.customer_id == current_customer.id,
            CartItem.product_id == cart.product_id
        )
        .first()
    )

    if existing_item:

        existing_item.quantity += cart.quantity

        db.commit()

        db.refresh(existing_item)

        return {
            "message": "Cart updated"
        }

    new_item = CartItem(
        customer_id=current_customer.id,
        product_id=cart.product_id,
        quantity=cart.quantity
    )

    db.add(new_item)

    db.commit()

    db.refresh(new_item)

    return {
        "message": "Added to cart",
        "cart_item_id": new_item.id
    }


@router.get(
    "/",
    response_model=list[CartResponse]
)
def get_cart(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    cart_items = (
        db.query(CartItem)
        .filter(
            CartItem.customer_id == current_customer.id
        )
        .all()
    )

    return cart_items


@router.put("/update/{cart_item_id}")
def update_cart_item(
    cart_item_id: int,
    cart: CartUpdate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.customer_id == current_customer.id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = (
        db.query(Product)
        .filter(
            Product.id == item.product_id
        )
        .first()
    )

    if cart.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    item.quantity = cart.quantity

    db.commit()

    db.refresh(item)

    return {
        "message": "Cart updated successfully"
    }


@router.delete("/remove/{cart_item_id}")
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.customer_id == current_customer.id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(item)

    db.commit()

    return {
        "message": "Item removed from cart"
    }


@router.delete("/clear")
def clear_cart(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    (
        db.query(CartItem)
        .filter(
            CartItem.customer_id == current_customer.id
        )
        .delete()
    )

    db.commit()

    return {
        "message": "Cart cleared successfully"
    }