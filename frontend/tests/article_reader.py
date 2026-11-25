"""Run after building the frontend, with Python Playwright and Chrome installed."""
import json
import sys
from email.message import Message
from pathlib import Path
from threading import Thread
from unittest.mock import patch

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))
from server import Reader, ThreadingHTTPServer


def fixture_article(url):
    if url.endswith('/offline'):
        raise OSError('Offline fixture')
    headers = Message()
    headers['Content-Type'] = 'text/html'
    paragraphs = [f'<p>Paragraph {i}. ' + 'Reading words. ' * 15 + '</p>' for i in range(1, 31)]
    return ('<article>' + ''.join(paragraphs) + '</article>').encode(), url, headers


def check_reader(page, url):
    entries = [
        dict(title=title, url='https://example.org/' + path, date='', summary='Saved excerpt.')
        for title, path in [('Long article', 'long'), ('Offline article', 'offline')]
    ]
    library = dict(language='en', theme='sos', feeds=[
        dict(url='https://example.org/feed', title='Source', articles=entries)
    ])
    page.goto(url)
    page.evaluate("(data) => localStorage.setItem('sos-my-feed.v1', JSON.stringify(data))", library)
    page.reload()
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


if __name__ == '__main__':
    with patch('articles.fetch_public', side_effect=fixture_article), sync_playwright() as playwright:
        with ThreadingHTTPServer(('127.0.0.1', 0), Reader) as server:
            Thread(target=server.serve_forever, daemon=True).start()
            try:
                browser = playwright.chromium.launch(channel='chrome')
                page = browser.new_page(viewport=dict(width=990, height=750))
                check_reader(page, f'http://127.0.0.1:{server.server_port}/')
                browser.close()
            finally:
                server.shutdown()
