"""Shared test setup: every test runs on its own empty data folder and never reaches the network."""

import os
import shutil
import tempfile
from pathlib import Path

# The app reads these when it is imported, so they are set before any `app` import.
_ROOT = Path(tempfile.mkdtemp(prefix="sos-my-feed-tests-"))
os.environ["SOS_MY_FEED_DATA_DIR"] = str(_ROOT / "data")
os.environ["SOS_MY_FEED_FRONTEND_DIST"] = str(_ROOT / "dist")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import articles, subscriptions  # noqa: E402
from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.paths import DATA_DIR, FRONTEND_DIST  # noqa: E402


def _no_network(*args, **kwargs):
    raise AssertionError("A test tried to reach the network; mock the call instead.")


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    """A fresh database and data folder, with fetching feeds and articles blocked unless mocked."""
    # Not ignoring errors: a file that cannot be removed (on Windows, one that is still open)
    # would quietly carry one test's data into the next.
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
    shutil.rmtree(FRONTEND_DIST, ignore_errors=True)
    init_db()
    monkeypatch.setattr(subscriptions, "download", _no_network)
    monkeypatch.setattr(articles, "fetch_public", _no_network)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
