"""Serving the built frontend."""

from threading import Thread
from urllib.request import urlopen

import server


def test_client_side_routes_get_the_index_page(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "DIST", tmp_path)
    (tmp_path / "index.html").write_text("<title>index</title>")
    (tmp_path / "app.js").write_text("app")
    with server.ThreadingHTTPServer(("127.0.0.1", 0), server.Reader) as httpd:
        Thread(target=httpd.serve_forever, daemon=True).start()
        try:
            base = f"http://127.0.0.1:{httpd.server_port}"
            assert urlopen(base + "/settings").read() == b"<title>index</title>"
            assert urlopen(base + "/app.js").read() == b"app"
        finally:
            httpd.shutdown()
