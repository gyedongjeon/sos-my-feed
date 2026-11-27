"""The subscriptions as OPML, the file feed readers use to move them from one to another."""

import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from .db import get_connection

router = APIRouter(prefix="/api")

# Far more than any list of subscriptions takes.
MAX_SIZE = 5 * 1024 * 1024


class Listed(BaseModel):
    title: str
    url: str


@router.get("/opml")
def export() -> Response:
    root = ET.Element("opml", version="2.0")
    ET.SubElement(ET.SubElement(root, "head"), "title").text = "SOS My Feed"
    body = ET.SubElement(root, "body")
    with get_connection() as conn:
        for feed in conn.execute("SELECT url, title FROM feeds ORDER BY id"):
            ET.SubElement(body, "outline", text=feed["title"], title=feed["title"], type="rss", xmlUrl=feed["url"])
    ET.indent(root)
    return Response(
        ET.tostring(root, encoding="UTF-8", xml_declaration=True),
        media_type="text/x-opml",
        headers={"Content-Disposition": 'attachment; filename="sos-my-feed.opml"'},
    )


@router.post("/opml", response_model=list[Listed])
async def read(request: Request) -> list[Listed]:
    """Lists the feeds an OPML file holds, in its order and folders included, without
    subscribing to them: the page subscribes to them as it does to those of the catalog."""
    data = await request.body()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="This file is too large.")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise HTTPException(status_code=422, detail="Not an OPML file.") from e
    if root.tag != "opml":
        raise HTTPException(status_code=422, detail="Not an OPML file.")
    listed: dict[str, Listed] = {}
    for outline in root.iter("outline"):
        url = (outline.get("xmlUrl") or "").strip()
        if urlsplit(url).scheme not in ("https", "http") or url in listed:
            continue
        title = (outline.get("text") or outline.get("title") or "").strip() or urlsplit(url).hostname or url
        listed[url] = Listed(title=title[:500], url=url)
    return list(listed.values())
