from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.address import Address
from app.models.customer import Customer

from app.schemas.address import AddressCreate

from app.routers.auth import get_current_customer

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


@router.post("/")
def add_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    new_address = Address(
        customer_id=current_customer.id,
        full_name=address.full_name,
        phone=address.phone,
        address_line=address.address_line,
        city=address.city,
        state=address.state,
        pincode=address.pincode,
        country=address.country
    )

    db.add(new_address)
    db.commit()
    db.refresh(new_address)

    return {
        "message": "Address added successfully",
        "address_id": new_address.id
    }


@router.get("/")
def get_addresses(
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    addresses = (
        db.query(Address)
        .filter(
            Address.customer_id ==
            current_customer.id
        )
        .all()
    )

    return addresses


@router.put("/default/{address_id}")
def set_default_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    address = (
        db.query(Address)
        .filter(
            Address.id == address_id,
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

    (
        db.query(Address)
        .filter(
            Address.customer_id ==
            current_customer.id
        )
        .update(
            {"is_default": False}
        )
    )

    address.is_default = True

    db.commit()

    return {
        "message": "Default address updated"
    }


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    address = (
        db.query(Address)
        .filter(
            Address.id == address_id,
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

    db.delete(address)
    db.commit()

    return {
        "message": "Address deleted successfully"
    }