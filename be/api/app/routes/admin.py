from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db, get_current_admin_user
from app.models.user import User
from app.models.order import Order
from app.models.engagement import Feedback, LoggingUserAction
from app.schemas.user import UserOut, UserAdminOut
from app.schemas.order import OrderOut
from app.schemas.engagement import FeedbackOut, LoggingActionOut


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserAdminOut])
async def get_all_users(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(select(User))
    return result.scalars().all()


@router.get("/orders", response_model=List[OrderOut])
async def get_all_orders(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(select(Order))
    return result.scalars().all()


@router.get("/feedbacks", response_model=List[FeedbackOut])
async def get_all_feedbacks(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(select(Feedback))
    return result.scalars().all()


@router.get("/logs", response_model=List[LoggingActionOut])
async def get_all_logs(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    result = await session.execute(select(LoggingUserAction))
    return result.scalars().all()
