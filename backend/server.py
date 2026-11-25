import http.client
import json
import xml.etree.ElementTree as ET
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from feeds import download

DIST = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'


class Reader(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def do_POST(self):
        if self.path != '/api/feed' or self.headers.get_content_type() != 'application/json':
            self.send_error(400)
            return
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size < 8192:
                raise ValueError()
            url = json.loads(self.rfile.read(size))['url']
            if not isinstance(url, str):
                raise ValueError()
            result = download(url)
            status = 200
        except (ValueError, KeyError, TypeError, OSError, http.client.HTTPException, ET.ParseError):
            result = {'error': 'Could not read this feed'}
            status = 422
        body = json.dumps(result).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    print('SOS My Feed — http://127.0.0.1:8000', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8000), Reader).serve_forever()
