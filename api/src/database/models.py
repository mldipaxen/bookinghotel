import enum
from datetime import date, datetime
from typing import List

from src.database.database import base
from sqlalchemy import DATE, DateTime, Enum, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserTypes(enum.Enum):
    admin = "admin"
    regular_user = "regular_user"


class RefreshTokenStorage(base):
    __tablename__ = "refresh_token_storage"

    id: Mapped[int] = mapped_column(primary_key=True)

    refresh_token: Mapped[str] = mapped_column()
    expired: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class User(base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()

    password: Mapped[str] = mapped_column()

    type: Mapped[UserTypes] = mapped_column(Enum(UserTypes), default="regular_user")

    reviews: Mapped[List["Review"]] = relationship(
        cascade="all,delete",
        lazy="joined",
    )
    bookings: Mapped[List["Booking"]] = relationship(
        cascade="all,delete",
        lazy="joined",
    )


class Hotel(base):
    __tablename__ = "hotel"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(nullable=True)
    stars: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(Float)
    
    photo: Mapped[str] = mapped_column(nullable=True)

    bookings: Mapped[List["Booking"]] = relationship(cascade="all,delete", uselist=True)


class Booking(base):
    __tablename__ = "booking"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    hotel_id: Mapped[int] = mapped_column(ForeignKey(Hotel.id))

    d: Mapped[date] = mapped_column(DATE(), nullable=True)

    create_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class Review(base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    hotel_id: Mapped[int] = mapped_column(ForeignKey(Hotel.id))
    name: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column(nullable=True)
    dt: Mapped[datetime] = mapped_column(DateTime(timezone=True))

