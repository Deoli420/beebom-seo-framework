"""
URL crawler for Beebom.

Discovers internal URLs by parsing sitemap.xml first, then crawling
the homepage for additional links. Results are de-duplicated and
stored in the SQLite database with a timestamp.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

from utils.db_logger import _connect

logger = logging.getLogger(__name__)

BASE_URL = "https://beebom.com"


def _ensure_crawl_table() -> None:
    """Create the crawled_urls table if it does not exist."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawled_urls (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            url       TEXT    NOT NULL UNIQUE,
            source    TEXT    NOT NULL DEFAULT 'unknown',
            crawled_at TEXT   NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _save_urls(urls: list[str], source: str) -> None:
    """Insert discovered URLs into the database (ignore duplicates)."""
    conn = _connect()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    for url in urls:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO crawled_urls (url, source, crawled_at) VALUES (?, ?, ?)",
                (url, source, now),
            )
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()


def crawl_sitemap(sitemap_url: str | None = None) -> list[str]:
    """Parse the XML sitemap and return all <loc> URLs.

    Args:
        sitemap_url: Override URL for the sitemap. Defaults to BASE_URL/sitemap.xml.

    Returns:
        List of URLs found in the sitemap.
    """
    sitemap_url = sitemap_url or f"{BASE_URL}/sitemap.xml"
    logger.info("Fetching sitemap: %s", sitemap_url)
    try:
        resp = requests.get(sitemap_url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Could not fetch sitemap: %s", exc)
        return []

    urls: list[str] = []
    try:
        root = ElementTree.fromstring(resp.content)
    except ElementTree.ParseError:
        logger.warning("Sitemap XML parse error")
        return []

    # Handle sitemap index (contains <sitemap><loc>…) and urlset (contains <url><loc>…).
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in root.findall(".//sm:loc", ns):
        if loc.text:
            url = loc.text.strip()
            # If this is a sub-sitemap, recurse.
            if url.endswith(".xml"):
                urls.extend(crawl_sitemap(url))
            else:
                urls.append(url)

    logger.info("Sitemap yielded %d URLs", len(urls))
    return urls


def crawl_homepage() -> list[str]:
    """Crawl the Beebom homepage and collect all internal href links.

    Returns:
        De-duplicated list of internal URLs.
    """
    logger.info("Crawling homepage: %s", BASE_URL)
    try:
        resp = requests.get(BASE_URL, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Could not fetch homepage: %s", exc)
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    urls = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        full = urljoin(BASE_URL, href)
        parsed = urlparse(full)
        if parsed.netloc in ("beebom.com", "www.beebom.com"):
            # Strip fragments and query strings for cleaner dedup.
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            urls.add(clean)

    logger.info("Homepage crawl yielded %d unique URLs", len(urls))
    return sorted(urls)


def discover_urls(max_urls: int = 500) -> list[str]:
    """Run the full discovery pipeline: sitemap + homepage crawl.

    Args:
        max_urls: Maximum number of URLs to return.

    Returns:
        De-duplicated, sorted list of internal beebom.com URLs.
    """
    _ensure_crawl_table()

    sitemap_urls = crawl_sitemap()
    homepage_urls = crawl_homepage()

    all_urls = sorted(set(sitemap_urls + homepage_urls))[:max_urls]
    _save_urls(all_urls, "crawler")

    logger.info("Total unique URLs discovered: %d", len(all_urls))
    return all_urls


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    urls = discover_urls()
    for u in urls[:20]:
        print(u)
    print(f"\n… {len(urls)} total URLs discovered")
