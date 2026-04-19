from a2wsgi import ASGIMiddleware

from app.main import app as asgi_app

# PythonAnywhere serves WSGI applications, so wrap FastAPI (ASGI) app.
application = ASGIMiddleware(asgi_app)
