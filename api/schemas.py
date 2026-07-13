from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class DestinationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_description: str | None
    description: str
    popularity_score: float
    latitude: float | None
    longitude: float | None
    source_url: str | None


class DestinationListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[DestinationOut]


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FavoriteCreate(BaseModel):
    destination_id: int
