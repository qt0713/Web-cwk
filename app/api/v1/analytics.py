from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.book import Book
from app.models.user import User


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/genres")
def genre_distribution(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = (
        db.query(Book.genre, func.count(Book.id).label("count"))
        .group_by(Book.genre)
        .order_by(func.count(Book.id).desc())
        .all()
    )
    return {"genres": [{"genre": genre, "count": count} for genre, count in rows]}


@router.get("/ratings")
def rating_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    total = db.query(func.count(Book.id)).scalar() or 0
    avg_rating = db.query(func.avg(Book.average_rating)).scalar()
    top_books = (
        db.query(Book)
        .order_by(Book.average_rating.desc(), Book.ratings_count.desc())
        .limit(5)
        .all()
    )

    return {
        "total_books": total,
        "average_rating": round(float(avg_rating), 3) if avg_rating is not None else None,
        "top_books": [
            {
                "id": b.id,
                "title": b.title,
                "genre": b.genre,
                "average_rating": b.average_rating,
                "ratings_count": b.ratings_count,
            }
            for b in top_books
        ],
    }
