import datetime
from typing import List
from sqlalchemy import ForeignKey, DateTime, Integer, UniqueConstraint, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .base import Base


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="carts", lazy="selectin")
    items: Mapped[List["CartItem"]] = relationship(
        back_populates="cart", lazy="selectin"
    )


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    custom_configuration: Mapped[dict] = mapped_column(JSON, nullable=True)

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="cascade"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="cascade"), nullable=False
    )

    cart: Mapped["Cart"] = relationship(back_populates="items", lazy="selectin")
    product: Mapped["Product"] = relationship(
        back_populates="in_carts", lazy="selectin"
    )
