"""Read public RSS and Atom feeds for the local reader."""
import http.client
import ipaddress
import re
import socket
import ssl
from pathlib import Path
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urljoin, urlsplit

LIMIT = 4 * 1024 * 1024


def download(url):
    for _ in range(5):
        parts = urlsplit(url)
        if parts.scheme not in ('https', 'http') or not parts.hostname or parts.username is not None:
            raise ValueError('Expected a public HTTP or HTTPS URL')
        secure = parts.scheme == 'https'
        port = parts.port or (443 if secure else 80)
        addresses = socket.getaddrinfo(parts.hostname, port, type=socket.SOCK_STREAM)
        address = addresses[0][4][0]
        if not ipaddress.ip_address(address).is_global or ipaddress.ip_address(address).is_multicast:
            raise ValueError('Expected a public host')
        if secure:
            context = ssl.create_default_context()
            system_bundle = Path('/etc/ssl/cert.pem')
            if not context.get_ca_certs() and system_bundle.is_file():
                context.load_verify_locations(str(system_bundle))
            connection = http.client.HTTPSConnection(parts.hostname, port, timeout=8, context=context)
        else:
            connection = http.client.HTTPConnection(parts.hostname, port, timeout=8)
        # Connect to the checked address, preserving the hostname for TLS and Host.
        connection._create_connection = lambda _, timeout, source: socket.create_connection((address, port), timeout)
        try:
            path = parts.path or '/'
            if parts.query:
                path += '?' + parts.query
            connection.request('GET', path, headers={'User-Agent': 'SOS-My-Feed/0.1'})
            response = connection.getresponse()
            if response.status in (301, 302, 303, 307, 308) and response.getheader('Location'):
                url = urljoin(url, response.getheader('Location'))
                continue
            if response.status != 200:
                raise ValueError('Feed unavailable')
            data = response.read(LIMIT + 1)
            if len(data) > LIMIT:
                raise ValueError('Feed too large')
            return parse_feed(data, url)
        finally:
            connection.close()
    raise ValueError('Too many redirects')


def parse_feed(data, url):
    root = ET.fromstring(data)
    atom = root.tag == '{http://www.w3.org/2005/Atom}feed'
    channel = root if atom else root.find('{*}channel')
    if channel is None:
        raise ValueError('Expected RSS or Atom')

    def field(node, *names):
        for name in names:
            child = node.find('{*}' + name)
            if child is not None:
                return ''.join(child.itertext()).strip()
        return ''

    entries = root.findall('{*}entry') if atom else channel.findall('{*}item') or root.findall('{*}item')
    articles = []
    seen = set()
    for entry in entries:
        link = field(entry, 'link')
        if atom:
            link = next((el.get('href') for el in entry.findall('{*}link') if el.get('rel', 'alternate') == 'alternate'), '')
        if not link:
            continue
        base = '{http://www.w3.org/XML/1998/namespace}base'
        href = urljoin(urljoin(urljoin(url, root.get(base, '')), entry.get(base, '')), link)
        if urlsplit(href).scheme not in ('https', 'http') or href in seen:
            continue
        seen.add(href)
        summary = unescape(re.sub('<[^>]*>', ' ', field(entry, 'summary', 'description', 'content', 'encoded')))
        articles.append(dict(title=field(entry, 'title')[:500] or href, url=href,
                             summary=' '.join(summary.split())[:300],
                             date=field(entry, 'published', 'pubDate', 'updated', 'date')))
        if len(articles) == 100:
            break
    return dict(title=field(channel, 'title')[:500] or urlsplit(url).hostname, articles=articles)
