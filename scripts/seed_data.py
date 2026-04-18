from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.book import Book


SAMPLE_BOOKS = [
    {
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Sci-Fi",
        "published_year": 1965,
        "average_rating": 4.6,
        "ratings_count": 1200,
        "description": "Epic science fiction set on Arrakis.",
    },
    {
        "title": "The Left Hand of Darkness",
        "author": "Ursula K. Le Guin",
        "genre": "Sci-Fi",
        "published_year": 1969,
        "average_rating": 4.4,
        "ratings_count": 800,
        "description": "Political and social sci-fi classic.",
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "genre": "Classic",
        "published_year": 1813,
        "average_rating": 4.5,
        "ratings_count": 2100,
        "description": "A timeless social satire.",
    },
]


def seed(db: Session):
    if db.query(Book).count() > 0:
        return
    db.add_all([Book(**item) for item in SAMPLE_BOOKS])
    db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed(session)
        print("Seed data inserted.")
    finally:
        session.close()
