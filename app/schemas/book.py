from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    genre: str = Field(min_length=1, max_length=120)
    published_year: int = Field(ge=1450, le=2100)
    average_rating: float = Field(ge=0, le=5)
    ratings_count: int = Field(ge=0)
    description: str = Field(default="", max_length=1500)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    genre: str | None = Field(default=None, min_length=1, max_length=120)
    published_year: int | None = Field(default=None, ge=1450, le=2100)
    average_rating: float | None = Field(default=None, ge=0, le=5)
    ratings_count: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=1500)


class BookResponse(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RecommendationResponse(BaseModel):
    seed_book_id: int
    recommendations: list[BookResponse]
