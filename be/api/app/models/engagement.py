import datetime, enum
from typing import List, Optional, Any
from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Text,
    Float,
    Integer,
    Boolean,
    Enum as SQLEnum,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class NotificationType(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    PROMOTION = "promotion"


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_feedback"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="cascade"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", backref="feedbacks", lazy="selectin")
    product: Mapped["Product"] = relationship(
        "Product", backref="feedbacks", lazy="selectin"
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type"),
        default=NotificationType.INFO,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(
        "User", backref="notifications", lazy="selectin"
    )


class LoggingUserAction(Base):
    __tablename__ = "logging_user_actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_action: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", backref="actions", lazy="selectin")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="cascade"), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped["User"] = relationship(
        "User", backref="recommendations", lazy="selectin"
    )
    product: Mapped["Product"] = relationship(
        "Product", backref="recommendations", lazy="selectin"
    )


class Wishlist(Base):
    __tablename__ = "wishlist"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product_wishlist"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="cascade"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", backref="wishlist", lazy="selectin")
    product: Mapped["Product"] = relationship(
        "Product", backref="in_wishlists", lazy="selectin"
    )
