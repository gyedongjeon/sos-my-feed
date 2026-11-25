"""The reader's preferences, stored in the database (single user, so one global set)."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .db import get_connection

router = APIRouter(prefix="/api")


class Settings(BaseModel):
    # The language of the pages. None until the reader (or the browser's language, on the
    # first visit) has chosen one.
    language: Literal["en", "ko"] | None = None
    # A theme of the pages by its name; empty follows the system.
    theme: Literal["", "sos", "sos-night"] = ""
    # The size of an article's text, in pixels.
    reader_size: int = Field(default=20, ge=16, le=32)


@router.get("/settings", response_model=Settings)
def get_settings() -> Settings:
    with get_connection() as conn:
        saved = {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM settings")}
    return Settings(**{key: value for key, value in saved.items() if key in Settings.model_fields})


@router.put("/settings", response_model=Settings)
def save_settings(body: Settings) -> Settings:
    with get_connection() as conn:
        for key, value in body.model_dump().items():
            if value is None:
                conn.execute("DELETE FROM settings WHERE key = ?", (key,))
            else:
                conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    return get_settings()
