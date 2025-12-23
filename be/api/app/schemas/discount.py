from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class DiscountType(str, Enum):
    PERCENT = "percent"
    FIXED = "fixed"


class DiscountBase(BaseModel):
    code: str = Field(..., max_length=255)
    value: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    discount_type: str  # using str for simplicity or Enum


class DiscountCreate(DiscountBase):
    pass


class DiscountOut(DiscountBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
