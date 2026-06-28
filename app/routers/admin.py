from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.schemas.order import OrderStatusUpdate
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.payment import PaymentStatusUpdate
from app.models.admin import Admin
from app.models.customer import Customer
from app.models.order import Order
from app.models.payment import Payment
from app.models.product import Product

from app.schemas.admin import (
    AdminRegister,
    AdminLogin
)

from app.utils.hashing import (
    hash_password,
    verify_password
)

from app.utils.token import (
    create_access_token,
    verify_token
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/admin/login"
)


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    role = payload.get("role")

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    email = payload.get("sub")

    admin = (
        db.query(Admin)
        .filter(
            Admin.email == email
        )
        .first()
    )

    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="Admin not found"
        )

    return admin


@router.post("/register")
def register_admin(
    admin: AdminRegister,
    db: Session = Depends(get_db)
):

    existing = (
        db.query(Admin)
        .filter(
            Admin.email == admin.email
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_admin = Admin(
        name=admin.name,
        email=admin.email,
        password=hash_password(
            admin.password
        )
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {
        "message": "Admin registered successfully"
    }


@router.post("/login")
def login_admin(
    admin: AdminLogin,
    db: Session = Depends(get_db)
):

    db_admin = (
        db.query(Admin)
        .filter(
            Admin.email == admin.email
        )
        .first()
    )

    if db_admin is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        admin.password,
        db_admin.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {
            "sub": db_admin.email,
            "role": "admin"
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db)
):

    total_customers = (
        db.query(Customer)
        .count()
    )

    total_products = (
        db.query(Product)
        .count()
    )

    total_orders = (
        db.query(Order)
        .count()
    )

    total_payments = (
        db.query(Payment)
        .count()
    )

    paid_payments = (
        db.query(Payment)
        .filter(
            Payment.payment_status == "Paid"
        )
        .all()
    )

    total_revenue = sum(
        payment.amount
        for payment in paid_payments
    )

    return {
        "total_customers": total_customers,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_payments": total_payments,
        "total_revenue": total_revenue
    }


@router.get("/customers")
def get_customers(
    db: Session = Depends(get_db)
):

    return db.query(Customer).all()


@router.get("/orders")
def get_orders(
    db: Session = Depends(get_db)
):

    return db.query(Order).all()


@router.get("/payments")
def get_payments(
    db: Session = Depends(get_db)
):

    return db.query(Payment).all()

@router.put("/orders/{order_id}")
def update_order_status(
    order_id: int,
    order: OrderStatusUpdate,
    db: Session = Depends(get_db)
):

    db_order = (
        db.query(Order)
        .filter(
            Order.id == order_id
        )
        .first()
    )

    if db_order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    db_order.status = order.status

    db.commit()
    db.refresh(db_order)

    return {
        "message": "Order status updated successfully",
        "order_id": db_order.id,
        "new_status": db_order.status
    }

@router.get("/payments")
def get_payments(
    db: Session = Depends(get_db)
):

    return db.query(Payment).all()

@router.put("/payments/{payment_id}")
def update_payment_status(
    payment_id: int,
    payment: PaymentStatusUpdate,
    db: Session = Depends(get_db)
):

    db_payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id
        )
        .first()
    )

    if db_payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    db_payment.payment_status = payment.payment_status

    db.commit()
    db.refresh(db_payment)

    return {
        "message": "Payment status updated successfully",
        "payment_id": db_payment.id,
        "payment_status": db_payment.payment_status
    }


@router.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(customer)
    db.commit()

    return {
        "message": "Customer deleted successfully"
    }

@router.put("/customers/{customer_id}/disable")
def disable_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer.is_active = False

    db.commit()
    db.refresh(customer)

    return {
        "message": "Customer disabled successfully"
    }

@router.put("/customers/{customer_id}/enable")
def enable_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id
        )
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer.is_active = True

    db.commit()
    db.refresh(customer)

    return {
        "message": "Customer enabled successfully"
    }


