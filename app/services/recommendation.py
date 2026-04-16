from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.book import Book


def get_recommendations(db: Session, seed_book_id: int, limit: int = 5) -> list[Book]:
    seed = db.query(Book).filter(Book.id == seed_book_id).first()
    if not seed:
        return []

    # Prioritize same-genre books and then globally top-rated books as fallback.
    same_genre = (
        db.query(Book)
        .filter(Book.genre == seed.genre, Book.id != seed.id)
        .order_by(desc(Book.average_rating), desc(Book.ratings_count))
        .limit(limit)
        .all()
    )

    if len(same_genre) >= limit:
        return same_genre

    remaining = limit - len(same_genre)
    fallback_ids = [book.id for book in same_genre] + [seed.id]

    fallback = (
        db.query(Book)
        .filter(Book.id.notin_(fallback_ids))
        .order_by(desc(Book.average_rating), desc(Book.ratings_count))
        .limit(remaining)
        .all()
    )

    return same_genre + fallback
