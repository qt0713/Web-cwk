# Book Metadata and Recommendation API Documentation

## Base URL
- Local: `http://127.0.0.1:8000`
- Prefix: `/api/v1`

## Authentication
Protected endpoints require Bearer token in header:
- `Authorization: Bearer <access_token>`

### Register User
- Method: `POST`
- Path: `/api/v1/auth/register`
- Request:
```json
{
  "username": "tester",
  "password": "StrongPass123"
}
```
- Response: `201 Created`

### Login
- Method: `POST`
- Path: `/api/v1/auth/login`
- Request:
```json
{
  "username": "tester",
  "password": "StrongPass123"
}
```
- Response: `200 OK`
```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

## Data Model: Book
```json
{
  "id": 1,
  "title": "Dune",
  "author": "Frank Herbert",
  "genre": "Sci-Fi",
  "published_year": 1965,
  "average_rating": 4.6,
  "ratings_count": 1200,
  "description": "Epic science fiction set on Arrakis.",
  "created_at": "2026-04-04T10:00:00",
  "updated_at": "2026-04-04T10:00:00"
}
```

## Endpoints

### 1) Create Book
- Method: `POST`
- Path: `/api/v1/books`
- Request:
```json
{
  "title": "Dune",
  "author": "Frank Herbert",
  "genre": "Sci-Fi",
  "published_year": 1965,
  "average_rating": 4.6,
  "ratings_count": 1200,
  "description": "Epic science fiction set on Arrakis."
}
```
- Response: `201 Created`

### 2) List Books
- Method: `GET`
- Path: `/api/v1/books`
- Query params:
  - `skip` (default 0)
  - `limit` (default 20, max 100)
  - `genre` (optional)
- Response: `200 OK`

### 3) Get Book by ID
- Method: `GET`
- Path: `/api/v1/books/{book_id}`
- Response: `200 OK`
- Not found: `404 Not Found`

### 4) Update Book
- Method: `PUT`
- Path: `/api/v1/books/{book_id}`
- Partial update supported (send changed fields only)
- Response: `200 OK`
- Not found: `404 Not Found`

### 5) Delete Book
- Method: `DELETE`
- Path: `/api/v1/books/{book_id}`
- Response: `204 No Content`
- Not found: `404 Not Found`

### 6) Get Recommendations
- Method: `GET`
- Path: `/api/v1/books/{book_id}/recommendations`
- Query params:
  - `limit` (default 5, max 20)
- Recommendation strategy:
  - First return same-genre books sorted by rating and number of ratings.
  - If insufficient, fill with globally top-rated books.
- Response: `200 OK`
```json
{
  "seed_book_id": 1,
  "recommendations": [
    {
      "id": 2,
      "title": "Neuromancer",
      "author": "William Gibson",
      "genre": "Sci-Fi",
      "published_year": 1984,
      "average_rating": 4.3,
      "ratings_count": 1100,
      "description": "Cyberpunk pioneer.",
      "created_at": "2026-04-04T10:00:00",
      "updated_at": "2026-04-04T10:00:00"
    }
  ]
}
```

### 7) Genre Distribution Analytics
- Method: `GET`
- Path: `/api/v1/analytics/genres`
- Response: `200 OK`
```json
{
  "genres": [
    {"genre": "Sci-Fi", "count": 12},
    {"genre": "Classic", "count": 5}
  ]
}
```

### 8) Rating Summary Analytics
- Method: `GET`
- Path: `/api/v1/analytics/ratings`
- Response: `200 OK`
```json
{
  "total_books": 17,
  "average_rating": 4.182,
  "top_books": [
    {
      "id": 3,
      "title": "Dune",
      "genre": "Sci-Fi",
      "average_rating": 4.6,
      "ratings_count": 1200
    }
  ]
}
```

## Health Check
- Method: `GET`
- Path: `/health`
- No authentication required
- Response:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

## Error Codes Summary
- `200 OK`: successful read/update request
- `201 Created`: successful create request
- `204 No Content`: successful delete request
- `401 Unauthorized`: invalid/missing token or invalid credentials
- `409 Conflict`: username already exists
- `404 Not Found`: requested resource not found
- `422 Unprocessable Entity`: request validation error
