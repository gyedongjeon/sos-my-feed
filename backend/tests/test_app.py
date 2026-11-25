"""Health check and serving the built frontend."""

from app.paths import FRONTEND_DIST


def build_frontend() -> None:
    (FRONTEND_DIST / "assets").mkdir(parents=True)
    (FRONTEND_DIST / "index.html").write_text("<title>index</title>")
    (FRONTEND_DIST / "assets" / "app.js").write_text("console.log('app')")


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_frontend_is_not_served_before_it_is_built(client):
    assert client.get("/").status_code == 404


def test_built_files_are_served(client):
    build_frontend()
    assert client.get("/").text == "<title>index</title>"
    assert client.get("/assets/app.js").text == "console.log('app')"


def test_client_side_routes_get_the_index_page(client):
    build_frontend()
    assert client.get("/settings").text == "<title>index</title>"


def test_unknown_api_paths_are_not_answered_with_the_index_page(client):
    build_frontend()
    assert client.get("/api/nope").status_code == 404


def test_files_outside_the_build_folder_are_not_served(client):
    build_frontend()
    (FRONTEND_DIST.parent / "secret.txt").write_text("secret")
    response = client.get("/..%2Fsecret.txt")
    assert "secret" not in response.text
