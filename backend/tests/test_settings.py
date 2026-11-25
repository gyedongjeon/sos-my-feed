"""The reader's preferences."""


def test_nothing_is_chosen_at_first(client):
    assert client.get("/api/settings").json() == {"language": None, "theme": "", "reader_size": 20}


def test_saved_settings_are_kept(client):
    chosen = {"language": "ko", "theme": "sos-night", "reader_size": 24}
    assert client.put("/api/settings", json=chosen).json() == chosen
    assert client.get("/api/settings").json() == chosen


def test_saving_replaces_what_was_saved(client):
    client.put("/api/settings", json={"language": "ko", "theme": "sos-night", "reader_size": 24})
    following_the_system = {"language": "en", "theme": "", "reader_size": 24}
    client.put("/api/settings", json=following_the_system)
    assert client.get("/api/settings").json() == following_the_system


def test_settings_the_pages_do_not_have_are_refused(client):
    valid = {"language": "en", "theme": "", "reader_size": 20}
    for wrong in ({"language": "fr"}, {"theme": "neon"}, {"reader_size": 15}, {"reader_size": 33}):
        assert client.put("/api/settings", json={**valid, **wrong}).status_code == 422
    assert client.get("/api/settings").json() == {"language": None, "theme": "", "reader_size": 20}
