"""Start the local reader used by the desktop packages."""
import sys
import webbrowser

from server import Reader, ThreadingHTTPServer


if __name__ == '__main__':
    with ThreadingHTTPServer(('127.0.0.1', 18371), Reader) as server:
        if '--browser' in sys.argv:
            print('SOS My Feed is running. Close this window to quit.', flush=True)
            webbrowser.open('http://127.0.0.1:18371/')
        else:
            print('ready', flush=True)
        server.serve_forever()
