from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.dependencies import get_db
from app.models.catalog_product import Discount
from app.schemas.discount import DiscountCreate, DiscountOut
from app.services.utils import commit_to_db

router = APIRouter(tags=["Discounts"])


@router.get("/discounts", response_model=List[DiscountOut])
async def get_discounts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Discount).where(Discount.is_active == True))
    return result.scalars().all()


@router.post("/discounts", response_model=DiscountOut)
async def create_discount(data: DiscountCreate, db: AsyncSession = Depends(get_db)):
    new_discount = Discount(**data.model_dump())
    db.add(new_discount)
    await commit_to_db(db)
    await db.refresh(new_discount)
    return new_discount
