import datetime, enum
from typing import List
from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Text,
    Float,
    Integer,
    Boolean,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Discount_Type(enum.Enum):
    percent: float
    fixed: float


from .base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    products: Mapped[List["Product"]] = relationship(
        back_populates="category", lazy="selectin"
    )
    parent: Mapped["Category"] = relationship(
        "Category", remote_side=[id], backref="children", lazy="selectin"
    )


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

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="restrict"), nullable=False
    )

    category: Mapped["Category"] = relationship(
        back_populates="products", lazy="selectin"
    )
    product_tags: Mapped[List["ProductTag"]] = relationship(
        back_populates="product", lazy="selectin"
    )
    in_carts: Mapped[List["CartItem"]] = relationship(
        back_populates="product", lazy="selectin"
    )
    in_orders: Mapped[List["OrderItem"]] = relationship(
        back_populates="product", lazy="selectin"
    )
    variants: Mapped[List["ProductVariant"]] = relationship(
        back_populates="product", lazy="selectin"
    )
    ingredients: Mapped[List["ProductIngredient"]] = relationship(
        back_populates="product", lazy="selectin"
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    product_tags: Mapped[List["ProductTag"]] = relationship(
        back_populates="tag", lazy="selectin"
    )


class ProductTag(Base):
    __tablename__ = "product_tags"
    __table_args__ = (UniqueConstraint("product_id", "tag_id", name="uq_product_tag"),)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="restrict"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="restrict"), primary_key=True
    )

    product: Mapped["Product"] = relationship(
        back_populates="product_tags", lazy="selectin"
    )
    tag: Mapped["Tag"] = relationship(back_populates="product_tags", lazy="selectin")


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


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="cascade"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[float] = mapped_column(Float, nullable=False)

    product: Mapped["Product"] = relationship(
        back_populates="variants", lazy="selectin"
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    calories_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    stock_quantity: Mapped[float] = mapped_column(Float, nullable=False)

    product_ingredients: Mapped[List["ProductIngredient"]] = relationship(
        back_populates="ingredient", lazy="selectin"
    )


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"
    __table_args__ = (
        UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="cascade"), nullable=False
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="cascade"), nullable=False
    )
    min_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    max_percentage: Mapped[float] = mapped_column(Float, nullable=True)

    product: Mapped["Product"] = relationship(
        back_populates="ingredients", lazy="selectin"
    )
    ingredient: Mapped["Ingredient"] = relationship(
        back_populates="product_ingredients", lazy="selectin"
    )
