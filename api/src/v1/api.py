from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_session
from src.database.models import User
from src.v1.auth import auth_router, login_required
from src.v1.hotel import hotel_router
from src.v1.review import review_router
from src.v1.user import user_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/user")
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(hotel_router, prefix="/hotel")
api_router.include_router(review_router, prefix="/review")


@api_router.get("/healthcheck")
async def index(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(select(User))
        return {"detail": "ok :)"}
    except Exception as e:
        print(e)
        return {"detail": "error"}


@api_router.get("/check_token")
async def token_checker(user=Depends(login_required)):
    return {"detail": "token is ok"}
