from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models.user import User, Address
from app.schemas.user import AddressCreate, AddressUpdate, AddressOut
from app.services.utils import commit_to_db

router = APIRouter(prefix="/users", tags=["User Address"])


@router.get("/me/addresses", response_model=List[AddressOut])
async def get_my_addresses(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Address).where(Address.user_id == current_user.id))
    return result.scalars().all()


@router.post("/me/addresses", response_model=AddressOut)
async def create_address(
    data: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check default
    if data.is_default:
        # unset others
        existing = await db.execute(
            select(Address).where(
                and_(Address.user_id == current_user.id, Address.is_default == True)
            )
        )
        for addr in existing.scalars():
            addr.is_default = False

    new_address = Address(user_id=current_user.id, **data.model_dump())
    db.add(new_address)
    await commit_to_db(db)
    await db.refresh(new_address)
    return new_address


@router.put("/me/addresses/{address_id}", response_model=AddressOut)
async def update_address(
    address_id: int,
    data: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Address).where(
            and_(Address.id == address_id, Address.user_id == current_user.id)
        )
    )
    address = result.scalar_one_or_none()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    update_data = data.model_dump(exclude_unset=True)
    if "is_default" in update_data and update_data["is_default"]:
        existing = await db.execute(
            select(Address).where(
                and_(Address.user_id == current_user.id, Address.is_default == True)
            )
        )
        for addr in existing.scalars():
            if addr.id != address_id:
                addr.is_default = False

    for key, value in update_data.items():
        setattr(address, key, value)

    await commit_to_db(db)
    await db.refresh(address)
    return address


@router.delete("/me/addresses/{address_id}")
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Address).where(
            and_(Address.id == address_id, Address.user_id == current_user.id)
        )
    )
    address = result.scalar_one_or_none()
    if address:
        await db.delete(address)
        await commit_to_db(db)
    return {"message": "Address deleted"}
