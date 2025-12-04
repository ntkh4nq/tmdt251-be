import datetime
from typing import List
from sqlalchemy import String, DateTime, ForeignKey, func, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hashed: Mapped[str] = mapped_column(String(255), nullable=False)
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", cascade="save-update, merge", lazy="selectin")
    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="save-update, merge", lazy="selectin")
    user_roles: Mapped[List["UserRole"]] = relationship(back_populates="user", cascade="save-update, merge", lazy="selectin")

class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    province: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="addresses", lazy="selectin")

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    refresh_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    device_info: Mapped[str] = mapped_column(String(255), nullable=False)
    expired_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="sessions", lazy="selectin")

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    roles: Mapped[List["UserRole"]] = relationship(back_populates="role", lazy="selectin")

class UserRole(Base): 
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="cascade"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="cascade"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="user_roles", lazy="selectin")
    role: Mapped["Role"] = relationship(back_populates="roles", lazy="selectin")
    