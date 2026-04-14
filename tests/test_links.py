"""
Link and image SEO tests for Beebom.

Checks for broken internal links, redirect chains, nofollow misuse,
and image alt attributes.
"""

import logging
from urllib.parse import urlparse

import allure
import pytest
import requests

from pages.base_page import BasePage
from data.urls import SMOKE_URLS

logger = logging.getLogger(__name__)

# Use a smaller URL set for link checks — they are network-intensive.
LINK_TEST_URLS = SMOKE_URLS


@pytest.mark.regression
@pytest.mark.parametrize("url", LINK_TEST_URLS)
class TestLinks:
    """Validate internal links and images on selected pages."""

    @allure.title("No broken internal links")
    def test_no_broken_internal_links(self, page, url):
        """All internal links should return HTTP 200."""
        bp = BasePage(page)
        bp.goto(url)
        links = bp.get_all_links()
        internal = [
            l["href"] for l in links
            if urlparse(l["href"]).netloc in ("", "beebom.com", "www.beebom.com")
            and l["href"].startswith("http")
        ]
        # Sample up to 20 links to keep runtime reasonable.
        broken = []
        for link in internal[:20]:
            try:
                resp = requests.head(link, timeout=10, allow_redirects=True)
                if resp.status_code >= 400:
                    broken.append((link, resp.status_code))
            except requests.RequestException as exc:
                broken.append((link, str(exc)))
        logger.info("[%s] Checked %d internal links, broken: %d", url, min(len(internal), 20), len(broken))
        assert not broken, f"Broken links on {url}: {broken}"

    @allure.title("No redirect chains longer than 2 hops")
    def test_no_redirect_chains(self, page, url):
        """Redirect chains waste crawl budget and slow page loads."""
        bp = BasePage(page)
        bp.goto(url)
        links = bp.get_all_links()
        internal = [
            l["href"] for l in links
            if urlparse(l["href"]).netloc in ("", "beebom.com", "www.beebom.com")
            and l["href"].startswith("http")
        ]
        chains = []
        for link in internal[:15]:
            try:
                resp = requests.head(link, timeout=10, allow_redirects=True)
                if len(resp.history) > 2:
                    chains.append((link, len(resp.history)))
            except requests.RequestException:
                pass
        assert not chains, f"Redirect chains on {url}: {chains}"

    @allure.title("Internal links do not use nofollow")
    def test_no_nofollow_internal(self, page, url):
        """Internal links should pass link equity — nofollow is wasteful."""
        bp = BasePage(page)
        bp.goto(url)
        links = bp.get_all_links()
        nofollowed = [
            l for l in links
            if urlparse(l["href"]).netloc in ("", "beebom.com", "www.beebom.com")
            and "nofollow" in l.get("rel", "")
            and l["href"].startswith("http")
            # Exclude self-referencing anchor links (#) — not a real SEO issue
            and not l["href"].endswith("#")
            and "#" not in urlparse(l["href"]).fragment
        ]
        assert not nofollowed, (
            f"Internal nofollow links on {url}: "
            f"{[l['href'] for l in nofollowed[:5]]}"
        )

    @allure.title("All images have an alt attribute")
    def test_images_have_alt(self, page, url):
        """Images without alt hurt accessibility and image SEO."""
        bp = BasePage(page)
        bp.goto(url)
        images = bp.get_image_alts()
        missing = [img for img in images if img["alt"] is None]
        logger.info("[%s] Images: %d, missing alt: %d", url, len(images), len(missing))
        assert not missing, (
            f"{len(missing)} images lack alt on {url}: "
            f"{[m['src'][:80] for m in missing[:5]]}"
        )

    @allure.title("Image alt attributes are not empty strings")
    def test_alt_not_empty(self, page, url):
        """An empty alt='' is almost as bad as a missing alt for SEO."""
        bp = BasePage(page)
        bp.goto(url)
        images = bp.get_image_alts()
        empty = [img for img in images if img["alt"] is not None and img["alt"].strip() == ""]
        # Decorative images are allowed empty alt — warn if many.
        if len(empty) > len(images) * 0.5 and len(images) > 3:
            pytest.fail(
                f"Over 50% of images have empty alt on {url} "
                f"({len(empty)}/{len(images)})"
            )

    @allure.title("No 404 images")
    def test_no_404_images(self, page, url):
        """All image src URLs should return HTTP 200."""
        bp = BasePage(page)
        bp.goto(url)
        images = bp.get_image_alts()
        broken = []
        for img in images[:20]:
            src = img.get("src", "")
            if not src or src.startswith("data:"):
                continue
            try:
                resp = requests.head(src, timeout=10, allow_redirects=True)
                if resp.status_code == 404:
                    broken.append(src)
            except requests.RequestException:
                pass
        assert not broken, f"404 images on {url}: {broken[:5]}"
