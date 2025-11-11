import datetime
from typing import List
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    passwrd: Mapped[str] = mapped_column(String(255), nullable=False)
    time_created: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    role: Mapped[str] = mapped_column(String(50), nullable=False)


