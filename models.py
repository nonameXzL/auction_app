from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="buyer")

    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")


class Lot(Base):
    __tablename__ = "lots"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    price: Mapped[int] = mapped_column(Integer)
    step: Mapped[int] = mapped_column(Integer)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    bids: Mapped[List["Bid"]] = relationship(back_populates="lot")


class Bid(Base):
    __tablename__ = "bids"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lot: Mapped["Lot"] = relationship(back_populates="bids")


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="notifications")