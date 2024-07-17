from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_session
from src.database.models import User
from src.v1.auth import login_required

user_router = APIRouter()


@user_router.get("/view")
async def user_view(
    user_id: int = None,
    user: User = Depends(login_required),
    session: AsyncSession = Depends(get_session),
):
    if user_id:
        user  = await session.get(User, user_id)
        return user.name
    else:
        user.password = ""
        return user
