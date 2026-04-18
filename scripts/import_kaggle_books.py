import argparse
import csv
import io
import subprocess
import tempfile
import zipfile
from pathlib import Path
import sys
import shutil
import time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.book import Book


def parse_year(publication_date: str | None) -> int:
    if not publication_date:
        return 2000
    parts = publication_date.strip().split("/")
    if parts and parts[-1].isdigit():
        year = int(parts[-1])
        if 1450 <= year <= 2100:
            return year
    return 2000


def safe_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value) if value not in (None, "") else default
    except ValueError:
        return default


def safe_int(value: str | None, default: int = 0) -> int:
    try:
        return int(float(value)) if value not in (None, "") else default
    except ValueError:
        return default


def normalize_key(key: str | None) -> str:
    if key is None:
        return ""
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def clean_value(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().strip('"')


def detect_csv_format(sample: str) -> str:
    # BX-Books.csv often uses ';' while Goodreads exports commonly use ','.
    return ";" if sample.count(";") > sample.count(",") else ","


def read_csv_text(csv_path: Path, preferred_names: list[str] | None = None) -> str:
    raw = csv_path.read_bytes()

    # Some downloads may still be ZIP archives even if named like CSV.
    if raw.startswith(b"PK\x03\x04"):
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            csv_names = [name for name in zf.namelist() if name.lower().endswith(".csv")]
            if not csv_names:
                raise RuntimeError(f"ZIP input does not contain any CSV file: {csv_path}")
            preferred = None
            if preferred_names:
                wanted = {x.lower() for x in preferred_names}
                for name in csv_names:
                    if Path(name).name.lower() in wanted:
                        preferred = name
                        break
            target = preferred or csv_names[0]
            raw = zf.read(target)

    # Some Kaggle exports are UTF-16 and include NUL bytes.
    if b"\x00" in raw:
        try:
            return raw.decode("utf-16")
        except UnicodeDecodeError:
            raw = raw.replace(b"\x00", b"")

    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace")


def iter_csv_rows(csv_text: str, delimiter: str):
    def _reader(text: str):
        sio = io.StringIO(text, newline="")
        return csv.DictReader(sio, delimiter=delimiter)

    try:
        for row in _reader(csv_text):
            yield row
        return
    except csv.Error:
        pass

    # Fallback: remove problematic null/newline artifacts and retry parsing.
    cleaned_lines = []
    for line in csv_text.splitlines():
        cleaned_lines.append(line.replace("\x00", "").replace("\r", ""))
    cleaned_text = "\n".join(cleaned_lines)

    for row in _reader(cleaned_text):
        yield row


def get_first(row: dict, keys: list[str]) -> str:
    for key in keys:
        if key in row and clean_value(row[key]):
            return clean_value(row[key])
    return ""


def parse_rows_from_path(csv_path: Path, preferred_names: list[str] | None = None):
    csv_text = read_csv_text(csv_path, preferred_names=preferred_names)
    sample = csv_text[:4096]
    delimiter = detect_csv_format(sample)
    return iter_csv_rows(csv_text, delimiter)


def build_ratings_map(ratings_csv_path: Path) -> dict[str, tuple[float, int]]:
    sums: dict[str, int] = {}
    counts: dict[str, int] = {}

    for row in parse_rows_from_path(ratings_csv_path, preferred_names=["ratings.csv", "bx-book-ratings.csv"]):
        normalized = {}
        for k, v in row.items():
            nk = normalize_key(k)
            if not nk:
                continue
            normalized[nk] = clean_value(v)

        isbn = get_first(normalized, ["isbn"])
        if not isbn:
            continue

        rating = safe_int(get_first(normalized, ["book_rating", "rating"]))
        # BX ratings: 0 often indicates implicit feedback, exclude from average.
        if rating <= 0:
            continue

        sums[isbn] = sums.get(isbn, 0) + rating
        counts[isbn] = counts.get(isbn, 0) + 1

    result: dict[str, tuple[float, int]] = {}
    for isbn, total in sums.items():
        cnt = counts[isbn]
        avg = round(total / cnt, 3)
        result[isbn] = (avg, cnt)
    return result


def map_row_to_book_fields(row: dict, source_label: str, ratings_map: dict[str, tuple[float, int]] | None = None) -> dict | None:
    normalized = {}
    for k, v in row.items():
        nk = normalize_key(k)
        if not nk:
            continue
        normalized[nk] = clean_value(v)

    title = get_first(normalized, ["title", "book_title"])
    author = get_first(normalized, ["authors", "author", "book_author"])

    if not title or not author:
        return None

    year_raw = get_first(normalized, ["publication_date", "year_of_publication", "published_year"])
    if "/" in year_raw:
        year = parse_year(year_raw)
    else:
        year = safe_int(year_raw, 2000)
        if not (1450 <= year <= 2100):
            year = 2000

    average_rating = max(
        0.0,
        min(
            5.0,
            safe_float(get_first(normalized, ["average_rating", "rating", "book_rating"]), 0.0),
        ),
    )
    ratings_count = max(0, safe_int(get_first(normalized, ["ratings_count", "rating_count"]), 0))

    isbn = get_first(normalized, ["isbn"])
    if ratings_map and isbn in ratings_map:
        average_rating, ratings_count = ratings_map[isbn]

    genre = get_first(normalized, ["genre", "category"])
    if not genre:
        genre = "General"

    publisher = get_first(normalized, ["publisher"])
    description = f"Imported from {source_label}"
    if publisher:
        description = f"Publisher: {publisher}. Source: {source_label}"

    return {
        "title": title[:255],
        "author": author[:255],
        "genre": genre[:120],
        "published_year": year,
        "average_rating": average_rating,
        "ratings_count": ratings_count,
        "description": description[:1500],
    }


def download_from_kaggle(dataset: str, file_name: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    kaggle_exe = shutil.which("kaggle")
    venv_kaggle = PROJECT_ROOT / ".venv" / "Scripts" / "kaggle.exe"
    if venv_kaggle.exists():
        kaggle_exe = str(venv_kaggle)
    if not kaggle_exe:
        raise RuntimeError("Kaggle CLI is not installed. Run: pip install kaggle")

    cmd = [
        kaggle_exe,
        "datasets",
        "download",
        "-d",
        dataset,
        "-f",
        file_name,
        "-p",
        str(output_dir),
        "--unzip",
    ]

    last_error = ""
    for attempt in range(1, 4):
        try:
            completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if completed.stdout.strip():
                print(completed.stdout.strip())
            break
        except subprocess.CalledProcessError as exc:
            details = "\n".join([x for x in [(exc.stderr or "").strip(), (exc.stdout or "").strip()] if x])
            last_error = details

            if "KeyError: 'username'" in details or "Could not find" in details:
                raise RuntimeError(
                    "Kaggle credentials are missing. Add kaggle.json to %USERPROFILE%/.kaggle/ or set KAGGLE_USERNAME and KAGGLE_KEY."
                ) from exc

            # Retry transient network failures.
            if "ConnectionResetError" in details or "Connection aborted" in details or "10054" in details:
                if attempt < 3:
                    time.sleep(2 * attempt)
                    continue

            raise RuntimeError(f"Kaggle download failed: {details}") from exc
    else:
        raise RuntimeError(f"Kaggle download failed after retries: {last_error}")

    csv_path = output_dir / file_name
    if not csv_path.exists():
        raise RuntimeError(f"Expected file not found after download: {csv_path}")
    return csv_path


def import_csv(
    db: Session,
    csv_path: Path,
    limit: int,
    replace: bool,
    ratings_csv_path: Path | None = None,
) -> tuple[int, int]:
    inserted = 0
    skipped = 0

    if replace:
        db.query(Book).delete()
        db.commit()

    source_label = csv_path.name
    ratings_map: dict[str, tuple[float, int]] | None = None

    if ratings_csv_path and ratings_csv_path.exists():
        ratings_map = build_ratings_map(ratings_csv_path)
        print(f"Loaded ratings map entries: {len(ratings_map)}")

    for idx, row in enumerate(parse_rows_from_path(csv_path, preferred_names=["books.csv", "bx-books.csv"])):
        if idx >= limit:
            break

        mapped = map_row_to_book_fields(row, source_label, ratings_map=ratings_map)
        if not mapped:
            skipped += 1
            continue

        title = mapped["title"]
        author = mapped["author"]

        exists = db.query(Book).filter(Book.title == title, Book.author == author).first()
        if exists:
            skipped += 1
            continue

        book = Book(**mapped)
        db.add(book)
        inserted += 1

    db.commit()
    return inserted, skipped


def main():
    parser = argparse.ArgumentParser(description="Import books from a Kaggle CSV dataset into the API database.")
    parser.add_argument("--dataset", default="arashnic/book-recommendation-dataset", help="Kaggle dataset slug")
    parser.add_argument("--file", default="Books.csv", help="CSV file name inside dataset")
    parser.add_argument("--limit", type=int, default=1000, help="Max rows to import")
    parser.add_argument("--replace", action="store_true", help="Delete existing books before import")
    parser.add_argument("--csv-path", default="", help="Use existing CSV path instead of downloading from Kaggle")
    parser.add_argument(
        "--ratings-csv-path",
        default="",
        help="Optional local ratings CSV path (e.g., Ratings.csv) for average/count enrichment",
    )
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    if args.csv_path:
        csv_path = Path(args.csv_path)
        if not csv_path.exists():
            raise SystemExit(f"CSV path not found: {csv_path}")
        ratings_csv_path = Path(args.ratings_csv_path) if args.ratings_csv_path else None
        if ratings_csv_path and not ratings_csv_path.exists():
            raise SystemExit(f"Ratings CSV path not found: {ratings_csv_path}")

        if not ratings_csv_path:
            sibling = csv_path.parent
            for candidate in ["Ratings.csv", "BX-Book-Ratings.csv"]:
                p = sibling / candidate
                if p.exists():
                    ratings_csv_path = p
                    break
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = download_from_kaggle(args.dataset, args.file, Path(temp_dir))
            ratings_csv_path = None
            for candidate in ["Ratings.csv", "BX-Book-Ratings.csv"]:
                try:
                    ratings_csv_path = download_from_kaggle(args.dataset, candidate, Path(temp_dir))
                    break
                except RuntimeError:
                    continue
            db = SessionLocal()
            try:
                inserted, skipped = import_csv(
                    db,
                    csv_path,
                    args.limit,
                    args.replace,
                    ratings_csv_path=ratings_csv_path,
                )
                print(f"Import completed. Inserted={inserted}, Skipped={skipped}")
                return
            finally:
                db.close()

    db = SessionLocal()
    try:
        inserted, skipped = import_csv(
            db,
            csv_path,
            args.limit,
            args.replace,
            ratings_csv_path=ratings_csv_path,
        )
        print(f"Import completed. Inserted={inserted}, Skipped={skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
