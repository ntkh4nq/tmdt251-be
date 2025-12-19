from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.engagement import Feedback, Notification, LoggingUserAction, Recommendation, Wishlist
from app.schemas.engagement import (
    FeedbackCreate, FeedbackOut,
    NotificationOut,
    LoggingActionCreate, LoggingActionOut,
    RecommendationOut,
    WishlistCreate, WishlistOut
)
from app.services.utils import commit_to_db

router = APIRouter(tags=["Engagement"])

# --- Feedback ---
@router.post("/feedback", response_model=FeedbackOut)
async def create_feedback(data: FeedbackCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_feedback = Feedback(
        user_id=current_user.id,
        **data.model_dump()
    )
    db.add(new_feedback)
    await commit_to_db(db)
    await db.refresh(new_feedback)
    return new_feedback

@router.get("/products/{product_id}/feedback", response_model=List[FeedbackOut])
async def get_product_feedback(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Feedback).where(Feedback.product_id == product_id))
    return result.scalars().all()

# --- Notifications ---
@router.get("/notifications", response_model=List[NotificationOut])
async def get_my_notifications(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()))
    return result.scalars().all()

@router.put("/notifications/{id}/read")
async def mark_notification_read(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Notification).where(and_(Notification.id == id, Notification.user_id == current_user.id)))
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await commit_to_db(db)
    return {"message": "Marked as read"}

# --- Wishlist ---
@router.get("/wishlist", response_model=List[WishlistOut])
async def get_wishlist(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Wishlist).where(Wishlist.user_id == current_user.id))
    return result.scalars().all()

@router.post("/wishlist", response_model=WishlistOut)
async def add_to_wishlist(data: WishlistCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if exists
    result = await db.execute(select(Wishlist).where(and_(Wishlist.user_id == current_user.id, Wishlist.product_id == data.product_id)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already in wishlist")
    
    item = Wishlist(user_id=current_user.id, product_id=data.product_id)
    db.add(item)
    await commit_to_db(db)
    await db.refresh(item)
    return item

@router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(product_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Wishlist).where(and_(Wishlist.user_id == current_user.id, Wishlist.product_id == product_id)))
    item = result.scalar_one_or_none()
    if item:
        await db.delete(item)
        await commit_to_db(db)
    return {"message": "Removed from wishlist"}

# --- Recommendations ---
@router.get("/recommendations", response_model=List[RecommendationOut])
async def get_recommendations(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Recommendation).where(Recommendation.user_id == current_user.id).order_by(Recommendation.score.desc()))
    return result.scalars().all()

# --- Logging ---
@router.post("/logs")
async def log_action(data: LoggingActionCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = LoggingUserAction(
        user_id=current_user.id,
        action_type=data.action_type,
        metadata_action=data.metadata_action
    )
    db.add(log)
    await commit_to_db(db)
    return {"message": "Logged"}
