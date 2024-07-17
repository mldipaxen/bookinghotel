from datetime import datetime

from pydantic import BaseModel


class ReviewAddSchema(BaseModel):
    name: str
    hotel_id: int
    text: str | None = None
