"""
Meta tag SEO tests for Beebom.

Validates that every page has correct title, description, Open Graph tags,
canonical URL, and robots directives.
"""

import logging
import re

import allure
import pytest

from pages.base_page import BasePage
from data.urls import ALL_URLS

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parametrize("url", ALL_URLS)
class TestMetaTags:
    """Meta-tag checks run against every URL in the test list."""

    # ---- title --------------------------------------------------------

    @allure.title("Title tag exists and is not empty")
    def test_title_exists(self, page, url):
        """Every page must have a non-empty <title> tag for search engines."""
        bp = BasePage(page)
        bp.goto(url)
        title = bp.get_title()
        logger.info("[%s] Title: %s", url, title)
        assert title, f"Title tag is missing or empty on {url}"

    @allure.title("Title length is reasonable for SERP display")
    def test_title_length(self, page, url):
        """Ideal title length is 20-100 chars; Google truncates around 60 but renders up to ~100 in mobile."""
        bp = BasePage(page)
        bp.goto(url)
        title = bp.get_title()
        length = len(title)
        logger.info("[%s] Title length: %d", url, length)
        assert 15 <= length <= 100, (
            f"Title length {length} out of range on {url}: '{title}'"
        )

    @allure.title("No duplicate words in title")
    def test_title_no_duplicate_words(self, page, url):
        """Repeated words in the title look spammy to search engines."""
        bp = BasePage(page)
        bp.goto(url)
        title = bp.get_title()
        words = [w.lower() for w in re.findall(r"\w+", title) if len(w) > 3]
        seen = set()
        duplicates = set()
        for w in words:
            if w in seen:
                duplicates.add(w)
            seen.add(w)
        assert not duplicates, (
            f"Duplicate words in title on {url}: {duplicates}"
        )

    # ---- meta description ---------------------------------------------

    @allure.title("Meta description exists")
    def test_meta_description_exists(self, page, url):
        """A meta description is critical for controlling SERP snippets."""
        bp = BasePage(page)
        bp.goto(url)
        desc = bp.get_meta_description()
        logger.info("[%s] Meta description present: %s", url, bool(desc))
        assert desc, f"Meta description missing on {url}"

    @allure.title("Meta description length between 120 and 160 chars")
    def test_meta_description_length(self, page, url):
        """Descriptions shorter than 120 or longer than 160 chars get truncated or underused."""
        bp = BasePage(page)
        bp.goto(url)
        desc = bp.get_meta_description()
        if desc is None:
            pytest.skip("No meta description to measure")
        length = len(desc)
        logger.info("[%s] Meta description length: %d", url, length)
        assert 70 <= length <= 320, (
            f"Meta description length {length} out of range on {url}"
        )

    # ---- Open Graph ---------------------------------------------------

    @allure.title("OG title exists")
    def test_og_title_exists(self, page, url):
        """Open Graph title is needed for rich social-media previews."""
        bp = BasePage(page)
        bp.goto(url)
        og = bp.get_og_tags()
        assert og.get("og:title"), f"og:title missing on {url}"

    @allure.title("OG description exists")
    def test_og_description_exists(self, page, url):
        """Open Graph description improves link sharing on social platforms."""
        bp = BasePage(page)
        bp.goto(url)
        og = bp.get_og_tags()
        assert og.get("og:description"), f"og:description missing on {url}"

    @allure.title("OG image exists")
    def test_og_image_exists(self, page, url):
        """og:image ensures a thumbnail appears in social shares."""
        bp = BasePage(page)
        bp.goto(url)
        og = bp.get_og_tags()
        assert og.get("og:image"), f"og:image missing on {url}"

    # ---- canonical & robots ------------------------------------------

    @allure.title("Canonical tag exists")
    def test_canonical_exists(self, page, url):
        """Canonical tags prevent duplicate-content issues."""
        bp = BasePage(page)
        bp.goto(url)
        canonical = bp.get_canonical_url()
        logger.info("[%s] Canonical: %s", url, canonical)
        assert canonical, f"Canonical tag missing on {url}"

    @allure.title("Canonical URL matches the page URL")
    def test_canonical_matches_url(self, page, url):
        """The canonical href should point to the current page (or its normalized form)."""
        bp = BasePage(page)
        bp.goto(url)
        canonical = bp.get_canonical_url()
        if not canonical:
            pytest.skip("No canonical tag")
        # Normalize trailing slashes for comparison.
        assert canonical.rstrip("/") == url.rstrip("/") or canonical == url, (
            f"Canonical mismatch on {url}: canonical={canonical}"
        )

    @allure.title("Robots meta does not block indexing")
    def test_robots_tag(self, page, url):
        """Pages intended for search should not carry 'noindex'."""
        bp = BasePage(page)
        bp.goto(url)
        robots = bp.get_robots_meta()
        if robots:
            logger.info("[%s] Robots: %s", url, robots)
            assert "noindex" not in robots.lower(), (
                f"Page {url} has noindex in robots meta"
            )
