from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer

from app.schemas.customer import CustomerRegister

from app.utils.hashing import (
    hash_password,
    verify_password
)

from app.utils.token import (
    create_access_token,
    verify_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_customer(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    email = payload.get("sub")

    customer = (
        db.query(Customer)
        .filter(Customer.email == email)
        .first()
    )

    if customer is None:
        raise HTTPException(
            status_code=401,
            detail="Customer not found"
        )

    return customer


@router.post("/register")
def register(
    customer: CustomerRegister,
    db: Session = Depends(get_db)
):

    existing_customer = (
        db.query(Customer)
        .filter(Customer.email == customer.email)
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_customer = Customer(
        name=customer.name,
        email=customer.email,
        password=hash_password(customer.password),
        phone=customer.phone
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {
        "message": "Customer registered successfully"
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_customer = (
        db.query(Customer)
        .filter(
            Customer.email == form_data.username
        )
        .first()
    )

    if not db_customer:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        db_customer.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {
            "sub": db_customer.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_profile(
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    return {
        "id": current_customer.id,
        "name": current_customer.name,
        "email": current_customer.email,
        "phone": current_customer.phone
    }