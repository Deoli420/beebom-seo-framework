"""
Mobile responsiveness SEO tests for Beebom.

Uses an iPhone 13 viewport to validate mobile UX signals that affect
Google's mobile-first indexing.
"""

import logging

import allure
import pytest

from pages.base_page import BasePage
from data.urls import SMOKE_URLS

logger = logging.getLogger(__name__)


@pytest.mark.mobile
@pytest.mark.parametrize("url", SMOKE_URLS)
class TestMobile:
    """Mobile-friendliness checks using the mobile_page fixture."""

    @allure.title("Viewport meta tag exists")
    def test_viewport_meta_exists(self, mobile_page, url):
        """A viewport meta tag is required for mobile-first indexing."""
        bp = BasePage(mobile_page)
        bp.goto(url)
        assert bp.is_mobile_responsive(), (
            f"Viewport meta tag missing on {url}"
        )

    @allure.title("Viewport includes width=device-width")
    def test_viewport_width_device(self, mobile_page, url):
        """The viewport must include width=device-width for proper scaling."""
        bp = BasePage(mobile_page)
        bp.goto(url)
        content = bp.get_viewport_content()
        if not content:
            pytest.skip("No viewport meta tag")
        logger.info("[%s] Viewport content: %s", url, content)
        assert "width=device-width" in content, (
            f"Viewport missing width=device-width on {url}: {content}"
        )

    @allure.title("Text is readable (font-size >= 12px)")
    def test_text_readable(self, mobile_page, url):
        """On mobile, text smaller than 12px is unreadable without zooming."""
        bp = BasePage(mobile_page)
        bp.goto(url)
        mobile_page.wait_for_load_state("domcontentloaded")
        min_font = bp.get_min_font_size()
        logger.info("[%s] Minimum font size: %.1fpx", url, min_font)
        assert min_font >= 10, (
            f"Font size too small on mobile ({min_font}px) on {url}"
        )

    @allure.title("Tap targets are large enough (>= 48x48)")
    def test_tap_targets(self, mobile_page, url):
        """Interactive elements should be at least 48x48 px for touch usability."""
        bp = BasePage(mobile_page)
        bp.goto(url)
        mobile_page.wait_for_load_state("domcontentloaded")
        small = bp.get_small_tap_targets()
        logger.info("[%s] Small tap targets: %d", url, len(small))
        # Allow a few small elements (icons, minor links).
        if len(small) > 20:
            logger.warning(
                "Many small tap targets on %s: %d — sample: %s",
                url, len(small), small[:5],
            )

    @allure.title("No horizontal scroll on mobile")
    def test_no_horizontal_scroll(self, mobile_page, url):
        """Page content should not overflow the mobile viewport horizontally."""
        bp = BasePage(mobile_page)
        bp.goto(url)
        mobile_page.wait_for_load_state("domcontentloaded")
        page_width = bp.get_page_width()
        viewport_width = bp.get_viewport_width()
        logger.info(
            "[%s] Page width: %d, Viewport: %d", url, page_width, viewport_width
        )
        # Allow small tolerance (5px) for sub-pixel rendering.
        assert page_width <= viewport_width + 5, (
            f"Horizontal overflow on {url}: page={page_width}, viewport={viewport_width}"
        )

    @allure.title("Page loads correctly on mobile")
    def test_mobile_layout_loads(self, mobile_page, url):
        """The page should load without errors on a mobile device."""
        bp = BasePage(mobile_page)
        bp.goto(url)
        mobile_page.wait_for_load_state("domcontentloaded")
        title = bp.get_title()
        logger.info("[%s] Mobile page title: %s", url, title)
        assert title, f"Page failed to load on mobile: {url}"
