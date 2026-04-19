# Book Metadata and Recommendation API

Coursework project for an individual API assessment with CRUD, recommendation logic, JWT authentication, analytics endpoints, testing, and presentation/report deliverables.

## Features
- Full CRUD for `Book` model in SQL database.
- Recommendation endpoint based on genre similarity and rating fallback.
- JWT authentication with register/login flow.
- Analytics endpoints for genre distribution and rating summary.
- Input validation and standard HTTP status codes.
- Pytest integration tests.
- Supporting materials for oral exam.

## Tech Stack
- FastAPI
- SQLAlchemy
- PostgreSQL (primary) or SQLite (local quick start)
- Pytest + TestClient

## Project Structure
```text
app/
  api/v1/auth.py
  api/v1/books.py
  api/v1/analytics.py
  core/config.py
  core/security.py
  db/
  models/book.py
  models/user.py
  schemas/book.py
  schemas/auth.py
  services/recommendation.py
  main.py
docs/
  API_DOCUMENTATION.md
tests/
  test_books_api.py
scripts/
  seed_data.py
```

## Quick Start
1. Create and activate virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` from `.env.example` and adjust values.
4. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Open docs:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

## PostgreSQL Setup (recommended)
1. Start database:
   ```bash
   docker compose up -d
   ```
2. Set in `.env`:
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/books_api
   ```

## Seed Sample Data
```bash
python scripts/seed_data.py
```

## Import Kaggle Dataset (Books)
This project includes an importer aligned to dataset-style coursework evidence.

Recommended dataset:
- `arashnic/book-recommendation-dataset`
- CSV file: `Books.csv`

1. Configure Kaggle credentials (choose one):
  - Put `kaggle.json` into `%USERPROFILE%/.kaggle/`
  - or set env vars `KAGGLE_USERNAME` and `KAGGLE_KEY`

2. Import up to 1000 rows:
  ```bash
  python scripts/import_kaggle_books.py --limit 1000
  ```

3. Replace existing books before import:
  ```bash
  python scripts/import_kaggle_books.py --limit 1000 --replace
  ```

If you downloaded CSV manually, import from local file:
```bash
python scripts/import_kaggle_books.py --csv-path path/to/Books.csv --replace
```

You can explicitly select dataset/file:
```bash
python scripts/import_kaggle_books.py --dataset arashnic/book-recommendation-dataset --file Books.csv --limit 1000 --replace
```

To merge rating statistics from `Ratings.csv` into `average_rating` and `ratings_count`:
```bash
python scripts/import_kaggle_books.py --csv-path .\Books.csv --ratings-csv-path .\Ratings.csv --limit 1000 --replace
```

### Dataset Import Evidence (Completed)
- Dataset: arashnic/book-recommendation-dataset
- File: Books.csv
- Command executed:
  ```bash
  python scripts/import_kaggle_books.py --csv-path .\Books.csv --limit 1000 --replace
  ```
- Result: Import completed. Inserted=1000, Skipped=0
- Verification command:
  ```bash
  python -c "import sys;from pathlib import Path;sys.path.insert(0,str(Path('.').resolve()));from app.db.session import SessionLocal;from app.models.book import Book;db=SessionLocal();print(db.query(Book).count());db.close()"
  ```
- Verification output: 1000

## End-to-End Testing (Current)
1. Start API:
  ```bash
  uvicorn app.main:app --reload --port 8000
  ```
2. Open website UI:
  - http://127.0.0.1:8000/
3. Open API docs:
  - http://127.0.0.1:8000/docs
4. In Swagger, test in order:
  - POST /api/v1/auth/register
  - POST /api/v1/auth/login
  - Authorize (OAuth2 popup: username/password)
  - GET /api/v1/books
  - POST /api/v1/books
  - GET /api/v1/books/{book_id}/recommendations
  - GET /api/v1/analytics/genres
  - GET /api/v1/analytics/ratings
5. Health endpoint:
  - http://127.0.0.1:8000/health

## Run Tests
```bash
pytest -q
```

## Example Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"tester\",\"password\":\"StrongPass123\"}"
```

Then call protected endpoints with:
```bash
-H "Authorization: Bearer <access_token>"
```

## API Documentation (PDF requirement)
- Source pdf: `docs/API_DOCUMENTATION.pdf`

## Pre-Submission Checklist
- [ ] Public GitHub repository URL added and accessible
- [ ] Commit history shows incremental progress (not one final commit)
- [ ] API docs exported to PDF and linked here
- [ ] Technical report completed (including GenAI declaration + dataset citation)
- [ ] Slides completed with architecture, docs, and demo evidence
- [ ] Live demo flow rehearsed (register/login -> CRUD -> recommendations -> analytics)

## Academic Integrity and GenAI
Use of GenAI must be declared. See `TECHNICAL_REPORT.pdf` section "Generative AI Declaration" and include conversation log excerpts in supplementary material.
