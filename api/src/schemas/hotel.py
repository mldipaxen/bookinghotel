from datetime import datetime
from pydantic import BaseModel


class HotelAddSchema(BaseModel):
    name: str
    location: str
    stars: int
    description: str
    price: float
    photo: str


class BookSchema(BaseModel):
    hotel_id: int
    d: datetime
