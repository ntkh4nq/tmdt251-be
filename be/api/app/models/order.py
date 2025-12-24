import datetime, enum
from typing import List
from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Float,
    Integer,
    UniqueConstraint,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Order_Status(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PRINTING = "printing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order_Payment_Status(enum.Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    REFUNDED = "refunded"


class Payment_Status(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Payment_Method(enum.Enum):
    COD = "cod"
    VNPAY = "vnpay"


class Shipment_Status(enum.Enum):
    PREPARING = "preparing"
    SHIPPING = "shipping"
    DELIVERED = "delivered"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[Order_Status] = mapped_column(
        SQLEnum(Order_Status, name="order_status"), default=Order_Status.PENDING
    )
    payment_status: Mapped[Order_Payment_Status] = mapped_column(
        SQLEnum(Order_Payment_Status, name="order_payment_status"),
        default=Order_Payment_Status.UNPAID,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id", ondelete="cascade"), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="orders", lazy="selectin")
    address: Mapped["Address"] = relationship(back_populates="orders", lazy="selectin")
    payments: Mapped[List["Payment"]] = relationship(
        back_populates="order", lazy="selectin"
    )
    shipments: Mapped[List["Shipment"]] = relationship(
        back_populates="order", lazy="selectin"
    )
    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", lazy="selectin"
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    paid_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[Payment_Status] = mapped_column(
        SQLEnum(Payment_Status, name="payment_status"), default=Payment_Status.PENDING
    )
    method: Mapped[Payment_Method] = mapped_column(
        SQLEnum(Payment_Method, name="payment_method"), default=Payment_Method.COD
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="cascade"), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="payments", lazy="selectin")


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tracking_code: Mapped[str] = mapped_column(String(255), unique=True)
    courier: Mapped[str] = mapped_column(String(255))
    shipped_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    status: Mapped[Shipment_Status] = mapped_column(
        SQLEnum(Shipment_Status, name="shipment_status"),
        default=Shipment_Status.PREPARING,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="cascade"), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="shipments", lazy="selectin")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("product_id", "order_id", name="uq_product_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    custom_configuration: Mapped[dict] = mapped_column(JSON, nullable=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="cascade"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="cascade"), nullable=False
    )

    order: Mapped["Order"] = relationship(back_populates="items", lazy="selectin")
    product: Mapped["Product"] = relationship(
        back_populates="in_orders", lazy="selectin"
    )
