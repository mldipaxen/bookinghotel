from config import HOST
from fastapi import Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_session


def phone_check(phone_number: str):
    if phone_number[0] in ["8", "7"]:
        phone_number = "+7" + phone_number[1:].lstrip(" ").rstrip(" ")

    phone_number = phone_number.replace("-", "").replace(" ", "")

    if len(phone_number) != 12:
        raise HTTPException(400, f"wrong phone number format: {phone_number}")

    return phone_number
