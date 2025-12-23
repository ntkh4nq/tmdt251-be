from typing import List
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


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
