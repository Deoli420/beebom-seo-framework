"""
Heading-structure SEO tests for Beebom.

Validates H1 uniqueness, non-empty headings, proper hierarchy,
and keyword presence in H1.
"""

import logging
import re
from urllib.parse import urlparse

import allure
import pytest

from pages.base_page import BasePage
from data.urls import ALL_URLS

logger = logging.getLogger(__name__)

# Page types that may legitimately have short/missing H1 or empty headings
_LISTING_PATTERNS = ("/category/", "/tag/", "/author/", "/page/")


def _is_listing_page(url: str) -> bool:
    """Return True if the URL is a category, tag, or archive listing."""
    return any(p in url for p in _LISTING_PATTERNS)


@pytest.mark.regression
@pytest.mark.parametrize("url", ALL_URLS)
class TestHeadings:
    """Heading hierarchy and content checks."""

    @allure.title("Exactly one H1 per page")
    def test_single_h1(self, page, url):
        """Search engines expect a single H1 as the primary page heading."""
        bp = BasePage(page)
        bp.goto(url)
        count = bp.get_h1_count()
        logger.info("[%s] H1 count: %d", url, count)
        if url.rstrip("/") == "https://beebom.com":
            # Homepages often have logo + heading — allow 1-2
            assert 1 <= count <= 2, f"Expected 1-2 H1, found {count} on homepage"
        else:
            assert count >= 1, f"No H1 found on {url}"
            if count > 1 and not _is_listing_page(url):
                pytest.fail(f"Expected 1 H1, found {count} on {url}")

    @allure.title("H1 is not empty")
    def test_h1_not_empty(self, page, url):
        """An empty H1 provides no value to users or crawlers."""
        bp = BasePage(page)
        bp.goto(url)
        h1_text = bp.get_h1_text()
        if _is_listing_page(url) and not h1_text:
            # Category/tag pages may render H1 via CSS — log warning but allow
            logger.warning("[%s] Listing page has empty/missing H1 text", url)
            pytest.skip("Listing page H1 may be CSS-rendered")
        assert h1_text, f"H1 is empty or missing on {url}"

    @allure.title("H1 length is reasonable")
    def test_h1_length(self, page, url):
        """H1 should be descriptive but concise."""
        bp = BasePage(page)
        bp.goto(url)
        h1_text = bp.get_h1_text()
        if not h1_text:
            pytest.skip("No H1 found")
        length = len(h1_text)
        logger.info("[%s] H1 length: %d — '%s'", url, length, h1_text[:60])
        # Tag/category pages often have very short H1 like "#AI"
        if _is_listing_page(url):
            assert length >= 1, f"H1 is blank on listing page {url}"
        else:
            assert 10 <= length <= 200, (
                f"H1 length {length} out of range on {url}: '{h1_text}'"
            )

    @allure.title("At least one H2 on article pages")
    def test_h2_exists(self, page, url):
        """Article pages should have H2 sub-headings for structure."""
        bp = BasePage(page)
        bp.goto(url)
        h2_list = bp.get_all_h2()
        logger.info("[%s] H2 count: %d", url, len(h2_list))
        # Listing and homepage may legitimately lack H2s
        if _is_listing_page(url) or url.rstrip("/") == "https://beebom.com":
            return
        assert len(h2_list) >= 1, f"No H2 headings found on {url}"

    @allure.title("H2 does not appear before H1")
    def test_heading_hierarchy(self, page, url):
        """Proper heading hierarchy: H1 should come before any H2."""
        bp = BasePage(page)
        bp.goto(url)
        headings = bp.get_all_headings()
        if not headings:
            pytest.skip("No headings found")
        h1_index = None
        h2_index = None
        for i, h in enumerate(headings):
            if h["tag"] == "h1" and h["text"] and h1_index is None:
                h1_index = i
            if h["tag"] == "h2" and h["text"] and h2_index is None:
                h2_index = i
        if h1_index is not None and h2_index is not None:
            assert h1_index < h2_index, (
                f"H2 appears before H1 on {url}"
            )

    @allure.title("No empty headings (H1-H3) on article pages")
    def test_no_empty_headings(self, page, url):
        """Empty headings confuse screen readers and waste crawl budget."""
        bp = BasePage(page)
        bp.goto(url)
        # Category/tag pages often have CSS-rendered headings — skip them
        if _is_listing_page(url):
            pytest.skip("Listing pages may use CSS-rendered headings")
        headings = bp.get_all_headings()
        empty = [h for h in headings if h["tag"] in ("h1", "h2", "h3") and not h["text"]]
        assert not empty, (
            f"{len(empty)} empty headings on {url}: {empty[:5]}"
        )

    @allure.title("H1 contains a topic-relevant word")
    def test_keyword_in_h1(self, page, url):
        """H1 should include at least one word from the URL slug as a relevance signal."""
        bp = BasePage(page)
        bp.goto(url)
        h1_text = bp.get_h1_text()
        if not h1_text:
            pytest.skip("No H1 found")
        path = urlparse(url).path.strip("/")
        if not path:
            return  # homepage — no slug to match

        # Strip common path prefixes like category/, tag/, puzzle/
        slug = path.split("/")[-1] if "/" in path else path
        if not slug:
            return

        slug_words = {w.lower() for w in slug.replace("-", " ").split() if len(w) > 2}
        # Clean H1: strip #, special chars for matching
        clean_h1 = re.sub(r"[^a-zA-Z0-9\s]", "", h1_text)
        h1_words = {w.lower() for w in clean_h1.split() if len(w) > 2}
        overlap = slug_words & h1_words

        logger.info("[%s] Slug words: %s | H1 words: %s | Overlap: %s",
                    url, slug_words, h1_words, overlap)

        if _is_listing_page(url):
            # Tag/category pages — more lenient matching
            # Check if any slug word is a substring of any H1 word or vice versa
            fuzzy_match = any(
                sw in hw or hw in sw
                for sw in slug_words for hw in h1_words
            )
            if not overlap and not fuzzy_match:
                logger.warning("[%s] Listing page H1 doesn't match slug", url)
            return  # don't hard-fail listing pages

        assert overlap, (
            f"H1 on {url} does not contain any URL slug keyword. "
            f"Slug words: {slug_words}, H1: '{h1_text}'"
        )
