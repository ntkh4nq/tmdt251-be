import datetime
import enum
from sqlalchemy import String, DateTime, Float, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Discount_Type(enum.Enum):
    percent = "percent"
    fixed = "fixed"


class Discount(Base):
    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    end_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    discount_type: Mapped[Discount_Type] = mapped_column(
        SQLEnum(Discount_Type, name="discount_type"), nullable=False
    )
