"""The reader's preferences, stored in the database (single user, so one global set)."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from .db import get_connection

router = APIRouter(prefix="/api")

# The intervals the reader can choose from; 0 refreshes only when asked.
REFRESH_MINUTES = (0, 15, 30, 60, 180)


class Settings(BaseModel):
    # The language of the pages. None until the reader (or the browser's language, on the
    # first visit) has chosen one.
    language: Literal[
        "en", "ko", "ja", "zh-Hans", "zh-Hant", "es", "fr", "de", "it", "pt",
        "pl", "ru", "uk", "tr", "vi", "th", "id", "hi", "bn",
    ] | None = None
    # A theme of the pages by its name; empty follows the system.
    theme: Literal["", "sos", "sos-night"] = ""
    # How an article is laid out for reading: the paper's colour, the size of the text in
    # pixels, the height of a line in text sizes, the margins above and beside the text in
    # pixels, and whether one page or two are shown side by side.
    reader_theme: Literal["light", "sepia", "mint", "forest", "gray", "dark"] = "light"
    reader_size: int = Field(default=20, ge=14, le=32)
    reader_line_height: float = Field(default=1.8, ge=1.2, le=2.4)
    reader_margin_v: int = Field(default=80, ge=40, le=120)
    reader_margin_h: int = Field(default=40, ge=20, le=80)
    reader_pages: int = Field(default=1, ge=1, le=2)
    # Whether the reader has been shown how pages are turned.
    reader_tutorial_seen: bool = False
    # How often the feeds are read again while the app is open, in minutes; 0 never.
    refresh_minutes: int = 30

    @field_validator("refresh_minutes")
    @classmethod
    def _offered(cls, minutes: int) -> int:
        # An int rather than a Literal, since the database gives back the text "30".
        if minutes not in REFRESH_MINUTES:
            raise ValueError(f"Expected one of {REFRESH_MINUTES}")
        return minutes


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
