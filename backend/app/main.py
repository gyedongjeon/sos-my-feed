"""FastAPI entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .articles import router as articles_router
from .db import init_db
from .paths import FRONTEND_DIST
from .settings import router as settings_router
from .subscriptions import router as subscriptions_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="sos-my-feed", lifespan=lifespan)
app.include_router(articles_router)
app.include_router(settings_router)
app.include_router(subscriptions_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Lets the desktop shell know the server is ready."""
    return {"status": "ok"}


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str) -> FileResponse:
    """Serve the built frontend, so the whole app runs from this one server."""
    index = FRONTEND_DIST / "index.html"
    if path.startswith("api/") or not index.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    file = (FRONTEND_DIST / path).resolve()
    if file.is_file() and file.is_relative_to(FRONTEND_DIST.resolve()):
        return FileResponse(file)
    # Any other path is a client-side route; the Vue router takes it from here.
    return FileResponse(index)
