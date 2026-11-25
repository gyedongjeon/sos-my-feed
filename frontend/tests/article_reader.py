"""Reads articles in Chrome, against the real backend with the web replaced by fixtures.

Run after building the frontend, with Chrome installed:
    uv run --project backend --with playwright==1.58.0 python frontend/tests/article_reader.py
"""
import os
import socket
import sys
import tempfile
import time
from email.message import Message
from pathlib import Path
from threading import Thread
from unittest.mock import patch
from urllib.request import urlopen

import uvicorn
from playwright.sync_api import expect, sync_playwright

# The app reads this when it is imported, so it is set before any `app` import.
os.environ["SOS_MY_FEED_DATA_DIR"] = tempfile.mkdtemp(prefix="sos-my-feed-browser-")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


def fixture_article(url):
    if url.endswith('/offline'):
        raise OSError('Offline fixture')
    headers = Message()
    headers['Content-Type'] = 'text/html'
    paragraphs = [f'<p>Paragraph {i}. ' + 'Reading words. ' * 15 + '</p>' for i in range(1, 31)]
    return ('<article>' + ''.join(paragraphs) + '</article>').encode(), url, headers


def fixture_feed(url):
    entries = [
        dict(title=title, url='https://example.org/' + path, date='', summary='Saved excerpt.')
        for title, path in [('Long article', 'long'), ('Offline article', 'offline')]
    ]
    return dict(title='Source', articles=entries)


def subscribe():
    """What the reader did before: chose English and the light theme, and subscribed to a feed."""
    with TestClient(app) as client:
        assert client.put('/api/settings', json=dict(language='en', theme='sos', reader_size=20)).status_code == 200
        assert client.post('/api/feeds', json=dict(url='https://example.org/feed')).status_code == 201


def check_reader(page, url):
    page.goto(url)
    opener = page.get_by_role('button', name='Source Long article')
    opener.click()
    dialog = page.get_by_role('dialog')
    expect(dialog.get_by_text('Paragraph 30.', exact=False)).to_be_attached()
    forward = dialog.get_by_role('button', name='Next')
    forward.click()
    sheet = dialog.locator('article')
    assert sheet.evaluate('el => el.scrollLeft === el.clientWidth')
    page.keyboard.press('ArrowLeft')
    expect(dialog.get_by_role('button', name='Previous')).to_be_disabled()
    dialog.get_by_role('button', name='Increase text size').click()
    expect(sheet).to_have_css('font-size', '22px')

    page.set_viewport_size(dict(width=375, height=640))
    # Bound page turns so a navigation regression fails promptly.
    for _ in range(100):
        if not forward.is_enabled():
            break
        forward.click()
    expect(forward).to_be_disabled()
    assert sheet.evaluate('el => Math.abs(el.scrollLeft + el.clientWidth - el.scrollWidth) < 2')
    page.keyboard.press('Escape')
    expect(dialog).to_have_count(0)
    expect(opener).to_be_focused()

    page.get_by_role('button', name='Source Offline article').click()
    expect(dialog.get_by_text('Saved excerpt.', exact=True)).to_be_visible()
    dialog.get_by_role('button', name='Back to feed').click()
    expect(dialog).to_have_count(0)
    assert len(page.context.pages) == 1
    assert page.url == url

    # The settings page has an address of its own, which opens it directly.
    page.get_by_role('link', name='Settings').click()
    assert page.url == url + 'settings'
    page.reload()
    expect(page.get_by_role('heading', name='Subscriptions')).to_be_visible()


if __name__ == '__main__':
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port, log_level='warning'))
    with (
        patch('app.articles.fetch_public', side_effect=fixture_article),
        patch('app.subscriptions.download', side_effect=fixture_feed),
        sync_playwright() as playwright,
    ):
        subscribe()
        Thread(target=server.run, daemon=True).start()
        address = f'http://127.0.0.1:{port}/'
        try:
            for _ in range(100):
                try:
                    urlopen(address + 'api/health')
                    break
                except OSError:
                    time.sleep(0.1)
            browser = playwright.chromium.launch(channel='chrome')
            page = browser.new_page(viewport=dict(width=990, height=750))
            check_reader(page, address)
            browser.close()
        finally:
            server.should_exit = True
