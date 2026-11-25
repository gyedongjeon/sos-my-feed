# SOS My Feed

A local reader for RSS and Atom news and blog feeds in the SOS app series. [한국어](README.ko.md)

## Run

Download an installer from [GitHub Releases](https://github.com/gyedongjeon/sos-my-feed/releases).

- **macOS (Apple Silicon)** — Open the DMG, drag SOS My Feed into Applications, and open the app.
- **Windows (x64)** — Run the Setup EXE, then open SOS My Feed from Start. The reader opens in your default browser. Close its console window to stop the server.

Both installers include Python and the built frontend.

With a release ZIP, extract it and run `python3 backend/server.py` from the extracted folder with Python 3.12. The ZIP includes the built frontend.

To build from source, use Python 3.12 and Node.js 22.12 or later with npm. From the repository root:

```sh
(cd frontend && npm ci && npm run build)
python3 backend/server.py
```

Open http://127.0.0.1:8000, paste a public RSS or Atom feed URL, then subscribe.
Select a source or view all posts by date. Open an article to read the original.
Refresh retrieves the current feed entries (up to 100 per source). A failed refresh retains the previous entries.
Settings includes subscription removal, English and Korean, and system, light and dark themes.
Subscriptions, cached entries and settings are stored in the current browser profile and origin.

## Development

Run the backend as above. For frontend hot reload run `cd frontend && npm run dev` and use the URL printed by Vite.
Run `python3 -m unittest discover -s backend` for offline parser tests and `cd frontend && npm run build` for type checking and bundling.
See [AGENTS.md](AGENTS.md) for the working agreement and Git workflow.
