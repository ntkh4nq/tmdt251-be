import datetime, enum
from typing import List
from sqlalchemy import ForeignKey, String, DateTime, Text, Float, Integer, Boolean, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Discount_Type(enum.Enum):
    percent: float
    fixed: float

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    products: Mapped[List["Product"]] = relationship(back_populates="category", lazy="selectin")

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    model_file: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(Text, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="restrict"), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="products", lazy="selectin")
    product_tags: Mapped[List["ProductTag"]] = relationship(back_populates="product", lazy="selectin")
    in_carts: Mapped[List["CartItem"]] = relationship(back_populates="product", lazy="selectin")
    in_orders: Mapped[List["CartItem"]] = relationship(back_populates="product", lazy="selectin")

class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    product_tags: Mapped[List["ProductTag"]] = relationship(back_populates="tag", lazy="selectin")

class ProductTag(Base):
    __tablename__ = "product_tags"
    __table_args__ = (UniqueConstraint("product_id", "tag_id", name="uq_product_tag"))

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="restrict"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="restrict"), nullable=False)

    product: Mapped["Product"] = relationship(back_populates="product_tags", lazy="selectin")
    tag: Mapped["Tag"] = relationship(back_populates="product_tags", lazy="selectin")

class Discount(Base):
    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    discount_type: Mapped[Discount_Type] = mapped_column(SQLEnum(Discount_Type), nullable=False)

    

