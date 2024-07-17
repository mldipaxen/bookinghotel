from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_session
from src.database.models import Booking, Hotel, User
from src.schemas.hotel import BookSchema, HotelAddSchema
from src.v1.auth import admin_required, login_required

hotel_router = APIRouter()


@hotel_router.get("/view")
async def hotel_view(
    hotel_id: int = None,
    session: AsyncSession = Depends(get_session),
):
    if not hotel_id:
        stmt = select(Hotel).order_by(Hotel.name)
        result = (await session.execute(stmt)).scalars().all()

    else:
        stmt = select(Hotel).where(Hotel.id == hotel_id)
        result = (await session.execute(stmt)).scalar_one_or_none()

    return result


@hotel_router.post("/add")
async def hotel_add(
    hotel: HotelAddSchema,
    user: User = Depends(admin_required),
    session: AsyncSession = Depends(get_session),
):
    new_hotel = Hotel(**hotel.model_dump())

    session.add(new_hotel)
    await session.commit()

    return {"detail": "hotel add success"}


@hotel_router.post("/book")
async def hotel_book(
    data: BookSchema,
    user: User = Depends(login_required),
    session: AsyncSession = Depends(get_session),
):
    hotel = await session.get(Hotel, data.hotel_id)

    if not hotel:
        raise HTTPException(
            status_code=400,
            detail="hotel not found",
        )

    db_booking = (
        await session.execute(
            select(Booking).where(
                Booking.hotel_id == data.hotel_id,
                Booking.user_id == user.id,
                Booking.d == data.d,
            )
        )
    ).scalar_one_or_none()

    if db_booking:
        raise HTTPException(
            status_code=400,
            detail="hotel already booked",
        )

    new_booking = Booking(
        user_id=user.id,
        hotel_id=data.hotel_id,
        d=data.d,
        create_dt=datetime.now(),
    )

    session.add(new_booking)
    await session.commit()

    return {"detail": "hotel book success"}


@hotel_router.post("/cancel")
async def hotel_book(
    booking_id: int,
    user: User = Depends(login_required),
    session: AsyncSession = Depends(get_session),
):
    booking = await session.get(Booking, booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=400,
            detail="booking not found",
        )
    
    await session.execute(delete(Booking).where(Booking.id == booking.id))
    await session.commit()

    return {"detail": "booking cancel success"}
