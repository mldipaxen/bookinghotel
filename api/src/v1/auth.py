from datetime import datetime, timedelta

from config import (
    ALGORITHM,
    AUTH_SECRET,
    AUTH_TOKEN_LIFE,
    REFRESH_TOKEN_LIFE,
    RT_SECRET,
)
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.templating import Jinja2Templates
from jwt import decode, encode
from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_session
from src.database.models import RefreshTokenStorage, User
from src.schemas.auth import LoginSchema, SignUpSchema
from werkzeug.security import check_password_hash, generate_password_hash

auth_router = APIRouter()


async def type_required(
    types: list,
    auth: str = Header(None),
    session: AsyncSession = Depends(get_session),
):
    data = None
    try:
        data = decode(auth, AUTH_SECRET, algorithms=[ALGORITHM])

        token_expired_time = datetime.strptime(data["expired"], "%Y-%m-%d %H:%M:%S.%f")

        if token_expired_time < datetime.now():
            raise Exception

    except:
        raise HTTPException(status_code=401, detail="token is invalid")

    user = await session.get(User, data["id"])

    if not user:
        raise HTTPException(status_code=400, detail="user not found")

    if user.type.name not in types and types != []:
        raise HTTPException(status_code=400, detail="not allowed")

    return user


async def login_required(
    auth: str = Header(None), session: AsyncSession = Depends(get_session)
):
    return await type_required([], auth, session)


async def admin_required(
    auth: str = Header(None), session: AsyncSession = Depends(get_session)
):
    return await type_required(["admin"], auth, session)


def make_token(user_id: int):
    return encode(
        payload={
            "id": user_id,
            "expired": str(datetime.now() + timedelta(hours=float(AUTH_TOKEN_LIFE))),
        },
        key=AUTH_SECRET,
        algorithm=ALGORITHM,
    )


def make_refresh_token(user_id: int):
    return encode(
        payload={
            "id": user_id,
            "expired": str(datetime.now() + timedelta(days=float(REFRESH_TOKEN_LIFE))),
        },
        key=RT_SECRET,
        algorithm=ALGORITHM,
    )


@auth_router.post("/login")
async def login_func(
    request: Request,
    data: LoginSchema,
    session: AsyncSession = Depends(get_session),
):
    data.email = data.email.lstrip(" ").rstrip(" ")
    data.password = data.password.lstrip(" ").rstrip(" ")

    stmt = select(User).where(
        func.lower(User.email) == data.email.lower(),
    )

    user = (await session.execute(stmt)).unique().scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="wrong auth data",
        )

    if not check_password_hash(user.password, data.password):
        raise HTTPException(
            status_code=400,
            detail="wrong auth data",
        )

    token = make_token(user.id)

    request.session["auth"] = token

    return {
        "token": token,
        "refresh_token": make_refresh_token(user.id),
        "type": user.type.name,
    }


@auth_router.post("/signup")
async def signup(
    data: SignUpSchema,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(User).where(func.lower(User.email) == data.email.lower())

    user = (await session.execute(stmt)).unique().scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=400,
            detail="user already exists",
        )

    user = User(
        **{
            "name": data.name,
            "phone": data.phone,
            "email": data.email,
            "password": generate_password_hash(data.password),
        }
    )

    session.add(user)
    await session.commit()

    return {"detail": "signup success"}


@auth_router.post("/refresh")
async def refresh(
    request: Request,
    token: str = Header(None),
    session: AsyncSession = Depends(get_session),
):
    try:
        token_data = decode(token, RT_SECRET, algorithms=[ALGORITHM])

        token_expired_time = datetime.strptime(
            token_data["expired"],
            "%Y-%m-%d %H:%M:%S.%f",
        )

        if token_expired_time < datetime.now():
            raise Exception

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="token is invalid",
        )

    token_db = (
        await session.execute(
            select(RefreshTokenStorage).where(
                RefreshTokenStorage.refresh_token == token,
            )
        )
    ).scalar_one_or_none()

    if token_db:
        raise HTTPException(
            status_code=400,
            detail="token is invalid",
        )

    user_id = token_data["id"]

    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="user not found",
        )

    stmt = insert(RefreshTokenStorage).values(
        {
            "refresh_token": token,
            "expired": token_expired_time,
        }
    )

    chore = delete(RefreshTokenStorage).where(
        RefreshTokenStorage.expired < datetime.now(),
    )

    await session.execute(stmt)
    await session.execute(chore)

    await session.commit()
    
    token = make_token(user_id)
    
    request.session["auth"] = token

    return {
        "token": token,
        "refresh_token": make_refresh_token(user_id),
        "type": user.type.name,
    }
