"""The reader's preferences."""

DEFAULTS = {
    "language": None,
    "theme": "",
    "reader_theme": "light",
    "reader_size": 20,
    "reader_line_height": 1.8,
    "reader_margin_v": 80,
    "reader_margin_h": 40,
    "reader_pages": 1,
    "reader_tutorial_seen": False,
    "refresh_minutes": 30,
}
CHOSEN = {
    "language": "ko",
    "theme": "sos-night",
    "reader_theme": "sepia",
    "reader_size": 24,
    "reader_line_height": 1.5,
    "reader_margin_v": 60,
    "reader_margin_h": 30,
    "reader_pages": 2,
    "reader_tutorial_seen": True,
    "refresh_minutes": 60,
}


def test_nothing_is_chosen_at_first(client):
    assert client.get("/api/settings").json() == DEFAULTS


def test_saved_settings_are_kept(client):
    assert client.put("/api/settings", json=CHOSEN).json() == CHOSEN
    assert client.get("/api/settings").json() == CHOSEN


def test_saving_replaces_what_was_saved(client):
    client.put("/api/settings", json=CHOSEN)
    following_the_system = {**CHOSEN, "language": "en", "theme": "", "reader_tutorial_seen": False}
    client.put("/api/settings", json=following_the_system)
    assert client.get("/api/settings").json() == following_the_system


def test_settings_the_pages_do_not_have_are_refused(client):
    valid = {**DEFAULTS, "language": "en"}
    wrong_choices = (
        {"language": "sv"},
        {"theme": "neon"},
        {"reader_theme": "pink"},
        {"reader_size": 13},
        {"reader_size": 33},
        {"reader_line_height": 1.1},
        {"reader_line_height": 2.5},
        {"reader_margin_v": 39},
        {"reader_margin_h": 81},
        {"reader_pages": 3},
        {"refresh_minutes": 7},
        {"refresh_minutes": -15},
    )
    for wrong in wrong_choices:
        assert client.put("/api/settings", json={**valid, **wrong}).status_code == 422, wrong
    assert client.get("/api/settings").json() == DEFAULTS


PAGE_LANGUAGES = ["en", "ko", "ja", "zh-Hans", "zh-Hant", "es", "fr", "de", "it", "pt",
                  "pl", "ru", "uk", "tr", "vi", "th", "id", "hi", "bn"]


def test_every_language_of_the_pages_can_be_chosen(client):
    for language in PAGE_LANGUAGES:
        assert client.put("/api/settings", json={**DEFAULTS, "language": language}).json()["language"] == language


def test_feeds_can_be_refreshed_at_any_offered_interval_or_never(client):
    for minutes in (0, 15, 30, 60, 180):
        assert client.put("/api/settings", json={**DEFAULTS, "refresh_minutes": minutes}).json()["refresh_minutes"] == minutes
        assert client.get("/api/settings").json()["refresh_minutes"] == minutes
