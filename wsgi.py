import os

from a2wsgi import ASGIMiddleware

from app.main import app as asgi_app

# Default environment values for simple WSGI hosting setups.
os.environ.setdefault("DATABASE_URL", "sqlite:///./books_api.sqlite3")
os.environ.setdefault("JWT_SECRET_KEY", "change-this-jwt-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("AUTO_CREATE_TABLES", "false")

# PythonAnywhere serves WSGI applications, so wrap FastAPI (ASGI) app.
application = ASGIMiddleware(asgi_app)
