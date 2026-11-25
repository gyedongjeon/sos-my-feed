"""Reads articles in Chrome, against the real backend with the web replaced by fixtures.

Run after building the frontend, with Chrome installed:
    uv run --project backend --with playwright==1.58.0 python frontend/tests/article_reader.py
"""
import os
import re
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


def tap(page, across):
    """A tap on the page, `across` of the way from its left edge to its right."""
    size = page.viewport_size
    page.mouse.click(size['width'] * across, size['height'] / 2)


def check_reader(page, url):
    page.goto(url)
    opener = page.get_by_role('button', name='Source Long article')
    opener.click()
    dialog = page.get_by_role('dialog')
    sheet = dialog.locator('article')
    counter = dialog.locator('.counter')
    expect(dialog.get_by_text('Paragraph 30.', exact=False)).to_be_attached()

    # The first article opens with a guide; a tap under it turns no page.
    expect(dialog.get_by_role('heading', name='Reading an article')).to_be_visible()
    dialog.get_by_role('button', name='Next', exact=True).click()
    dialog.get_by_role('button', name='Next', exact=True).click()
    dialog.get_by_role('button', name='All done').click()
    expect(dialog.get_by_role('heading', name='Finished reading?')).to_have_count(0)
    expect(counter).to_have_text(re.compile(r'^1 / \d+$'))
    single = int(counter.inner_text().split(' / ')[1])
    assert single > 3

    # A tap on the right turns forward, the left arrow key back, a tap on the left does nothing on the first page.
    tap(page, 0.9)
    expect(counter).to_have_text(f'2 / {single}')
    page.keyboard.press('ArrowLeft')
    expect(counter).to_have_text(f'1 / {single}')
    tap(page, 0.1)
    expect(counter).to_have_text(f'1 / {single}')

    # A tap on the middle shows the menu, and another hides it.
    menu = dialog.locator('.menu-bar')
    if 'shown' in menu.get_attribute('class'):
        tap(page, 0.5)
    expect(menu).not_to_have_class(re.compile('shown'))
    tap(page, 0.5)
    expect(menu).to_have_class(re.compile('shown'))

    # The view settings: paper colour, text size, and two pages side by side.
    dialog.get_by_role('button', name='View settings', exact=True).click()
    dialog.get_by_role('button', name='Sepia').click()
    expect(dialog).to_have_css('background-color', 'rgb(252, 246, 229)')
    dialog.get_by_role('slider', name='Text size').fill('22')
    expect(sheet).to_have_css('font-size', '22px')
    dialog.get_by_role('button', name='Two pages').click()
    expect(sheet).to_have_css('column-count', '2')
    # Each of the two pages is half as wide as the one was, less the space between them.
    assert sheet.evaluate('el => el.querySelector("p:last-child").getBoundingClientRect().width < el.clientWidth / 2')
    # Escape puts the settings away first; the article stays open.
    page.keyboard.press('Escape')
    expect(dialog.get_by_role('slider', name='Text size')).to_have_count(0)
    expect(dialog).to_be_visible()

    # A narrow window shows one page whatever was chosen, and the last page ends the turning.
    page.set_viewport_size(dict(width=375, height=640))
    expect(sheet).to_have_css('column-count', '1')
    last = int(counter.inner_text().split(' / ')[1])
    # Bound page turns so a navigation regression fails promptly.
    for _ in range(last + 5):
        tap(page, 0.9)
    expect(counter).to_have_text(f'{last} / {last}')
    # The end of the text is on it, once the page has slid in. A paragraph may run over two
    # pages, so each part of it is looked at.
    page.wait_for_function('''() => [...document.querySelector("dialog article p:last-child").getClientRects()]
        .some(part => part.left >= 0 && part.right <= innerWidth)''', timeout=5000)
    page.keyboard.press('Escape')
    expect(dialog).to_have_count(0)
    expect(opener).to_be_focused()

    # What was chosen is kept: after a reload the guide stays away and the paper is still sepia.
    page.set_viewport_size(dict(width=990, height=750))
    page.reload()
    page.get_by_role('button', name='Source Offline article').click()
    expect(dialog.get_by_text('Saved excerpt.', exact=True)).to_be_visible()
    expect(dialog.get_by_role('heading', name='Reading an article')).to_have_count(0)
    expect(dialog).to_have_css('background-color', 'rgb(252, 246, 229)')
    expect(sheet).to_have_css('font-size', '22px')
    with page.expect_download() as download:
        dialog.get_by_role('button', name='Download as Markdown').click()
    assert re.fullmatch(r'\d{4}-\d\d-\d\d_Offline_article\.md', download.value.suggested_filename)
    dialog.get_by_role('button', name='Close reader').click()
    expect(dialog).to_have_count(0)
    assert len(page.context.pages) == 1
    assert page.url == url

    # The settings page has an address of its own, which opens it directly.
    page.get_by_role('link', name='Settings').click()
    assert page.url == url + 'settings'
    page.reload()
    expect(page.get_by_role('heading', name='Subscriptions')).to_be_visible()

    # The settings page credits the work the app is built with, and links the licenses it ships.
    expect(page.get_by_role('heading', name='Open source')).to_be_visible()
    expect(page.get_by_text('© 2025 Astral Software Inc.')).to_be_visible()
    notices = page.get_by_role('link', name='Full license texts').get_attribute('href')
    with urlopen(url + notices.lstrip('/')) as response:
        assert b'SIL Open Font License' in response.read()


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
