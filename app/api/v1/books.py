from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookResponse, BookUpdate, RecommendationResponse
from app.services.recommendation import get_recommendations


router = APIRouter(prefix="/books", tags=["Books"])


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    payload: BookCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    book = Book(**payload.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("", response_model=list[BookResponse])
def list_books(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    genre: str | None = None,
):
    query = db.query(Book)
    if genre:
        query = query.filter(Book.genre == genre)
    return query.offset(skip).limit(limit).all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    payload: BookUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(book, key, value)

    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    db.delete(book)
    db.commit()
    return None


@router.get("/{book_id}/recommendations", response_model=RecommendationResponse)
def recommend_books(
    book_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    limit: int = Query(default=5, ge=1, le=20),
):
    seed = db.query(Book).filter(Book.id == book_id).first()
    if not seed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    recs = get_recommendations(db=db, seed_book_id=book_id, limit=limit)
    return RecommendationResponse(seed_book_id=book_id, recommendations=recs)
