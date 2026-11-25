import tempfile
import unittest
from pathlib import Path
from threading import Thread
from unittest.mock import patch
from urllib.request import urlopen

import server


class ServerTests(unittest.TestCase):
    def test_client_side_routes_get_the_index_page(self):
        with tempfile.TemporaryDirectory() as dist, patch.object(server, 'DIST', Path(dist)):
            (Path(dist) / 'index.html').write_text('<title>index</title>')
            (Path(dist) / 'app.js').write_text('app')
            with server.ThreadingHTTPServer(('127.0.0.1', 0), server.Reader) as httpd:
                Thread(target=httpd.serve_forever, daemon=True).start()
                try:
                    base = f'http://127.0.0.1:{httpd.server_port}'
                    self.assertEqual(urlopen(base + '/settings').read(), b'<title>index</title>')
                    self.assertEqual(urlopen(base + '/app.js').read(), b'app')
                finally:
                    httpd.shutdown()
