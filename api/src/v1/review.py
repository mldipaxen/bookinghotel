from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, desc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_session
from src.database.models import Review, User
from src.schemas.review import ReviewAddSchema
from src.v1.auth import login_required

review_router = APIRouter()


@review_router.post("/add")
async def review_add(
    review: ReviewAddSchema,
    user: User = Depends(login_required),
    session: AsyncSession = Depends(get_session),
):
    stmt = insert(Review).values(
        {
            "user_id": user.id,
            "hotel_id": review.hotel_id,
            "name": review.name,
            "text": review.text,
            "dt": datetime.now(),
        }
    )

    await session.execute(stmt)
    await session.commit()

    return {"detail": "review add success"}

@review_router.post("/deletereview")
async def review_del(
    review_id: int,
    user: User = Depends(login_required),
    session: AsyncSession = Depends(get_session),
):
    review = await session.get(Review, review_id)
    
    if not review:
        raise HTTPException(
            status_code=400,
            detail="review not found",
        )
    
    await session.execute(delete(Review).where(Review.id == review.id))
    await session.commit()

    return {"detail": "review cancel success"}


@review_router.get("/view")
async def review_view(
    user_id: int = None,
    hotel_id: int = None,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Review).order_by(desc(Review.dt))

    if user_id:
        stmt = stmt.where(Review.user_id == user_id)

    if hotel_id:
        stmt = stmt.where(Review.hotel_id == hotel_id)

    result = await session.execute(stmt)

    return result.scalars().all()
