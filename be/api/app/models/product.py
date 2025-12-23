from typing import List
from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


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
