from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional, Any, Dict
from enum import Enum

class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    PROMOTION = "promotion"

# --- Feedback ---
class FeedbackBase(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackOut(FeedbackBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Notification ---
class NotificationBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    type: NotificationType = NotificationType.INFO

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationOut(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Logging ---
class LoggingActionCreate(BaseModel):
    action_type: str
    metadata_action: Optional[Dict[str, Any]] = None

class LoggingActionOut(LoggingActionCreate):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Recommendation ---
class RecommendationOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    score: float
    model_config = ConfigDict(from_attributes=True)

# --- Wishlist ---
class WishlistBase(BaseModel):
    product_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistOut(WishlistBase):
    id: int
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
