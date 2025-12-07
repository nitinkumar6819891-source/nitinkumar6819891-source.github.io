#!/usr/bin/env python3
"""
Fetch Medium RSS for @nitinkumar6819891, parse and write projects.json
"""
import feedparser
import json
from html import unescape
from datetime import datetime
import sys

# CONFIG
MEDIUM_RSS = "https://medium.com/feed/@nitinkumar6819891"
MAX_ITEMS = 8
OUT_FILE = "projects.json"

def excerpt_from_entry(entry, length=200):
    # entry.summary is HTML: strip tags simply
    text = entry.get('summary', '') or entry.get('content',[{}])[0].get('value','')
    # remove tags crudely:
    import re
    text = re.sub('<[^<]+?>', '', text)
    text = unescape(text).strip()
    if len(text) > length:
        return text[:length].rsplit(' ',1)[0] + "…"
    return text

def thumbnail_from_entry(entry):
    # try to find image in content
    if 'media_thumbnail' in entry:
        t = entry.media_thumbnail
        if isinstance(t, list):
            return t[0]['url']
        return t.get('url')
    # try to find first image in summary/content
    import re
    html = entry.get('content',[{}])[0].get('value','') or entry.get('summary','')
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    return None

def to_iso(dt_struct):
    try:
        return datetime(*dt_struct[:6]).strftime("%Y-%m-%d")
    except Exception:
        return ""

def main():
    feed = feedparser.parse(MEDIUM_RSS)
    if feed.bozo:
        print("Failed to parse feed:", feed.bozo_exception, file=sys.stderr)
    items = []
    for entry in feed.entries[:MAX_ITEMS]:
        title = entry.get('title','').strip()
        link = entry.get('link','').strip()
        date = to_iso(entry.get('published_parsed') or entry.get('updated_parsed') or '')
        excerpt = excerpt_from_entry(entry, 220)
        thumb = thumbnail_from_entry(entry) or ""
        items.append({
            "title": title,
            "link": link,
            "date": date,
            "excerpt": excerpt,
            "thumbnail": thumb
        })
    # write to OUT_FILE
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("Wrote", OUT_FILE)

if __name__ == "__main__":
    main()
