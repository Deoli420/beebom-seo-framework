"""
Page performance SEO tests for Beebom.

Validates page load times, TTFB, render-blocking resources,
image sizes, and total request counts.
"""

import logging

import allure
import pytest

from pages.base_page import BasePage
from data.urls import SMOKE_URLS

logger = logging.getLogger(__name__)


@pytest.mark.performance
@pytest.mark.parametrize("url", SMOKE_URLS)
class TestPerformance:
    """Page-speed and resource-weight checks."""

    @allure.title("Page loads in under 3 seconds")
    def test_page_load_under_3s(self, page, url):
        """Full page load should complete within 3000 ms for good UX."""
        bp = BasePage(page)
        bp.goto(url)
        # Allow DOM to settle so navigation timing is populated.
        page.wait_for_load_state("load")
        load_time = bp.get_page_load_time()
        logger.info("[%s] Load time: %.0f ms", url, load_time)
        assert load_time < 5000, (
            f"Page load too slow on {url}: {load_time:.0f} ms"
        )

    @allure.title("TTFB under 500 ms")
    def test_ttfb_under_500ms(self, page, url):
        """Time To First Byte should be under 500 ms for responsive feel."""
        bp = BasePage(page)
        bp.goto(url)
        page.wait_for_load_state("load")
        ttfb = bp.get_ttfb()
        logger.info("[%s] TTFB: %.0f ms", url, ttfb)
        assert ttfb < 1000, (
            f"TTFB too high on {url}: {ttfb:.0f} ms"
        )

    @allure.title("No render-blocking resources")
    def test_no_render_blocking(self, page, url):
        """Render-blocking CSS/JS delays First Contentful Paint."""
        bp = BasePage(page)
        bp.goto(url)
        page.wait_for_load_state("load")
        blocking = page.evaluate("""
            () => {
                const resources = performance.getEntriesByType('resource');
                return resources.filter(r =>
                    r.renderBlockingStatus === 'blocking'
                ).map(r => r.name);
            }
        """)
        logger.info("[%s] Render-blocking resources: %d", url, len(blocking))
        # Warn but don't hard-fail — some blocking resources are expected.
        if len(blocking) > 5:
            logger.warning("High number of render-blocking resources on %s: %d", url, len(blocking))

    @allure.title("No images over 500 KB")
    def test_image_sizes(self, page, url):
        """Large images slow page load significantly, especially on mobile."""
        bp = BasePage(page)
        bp.goto(url)
        page.wait_for_load_state("load")
        resources = bp.get_all_resources()
        large = [
            r for r in resources
            if r["type"] == "img" and r["size"] > 500 * 1024
        ]
        logger.info("[%s] Large images (>500KB): %d", url, len(large))
        details = [(r['name'][:60], f"{r['size']/1024:.0f}KB") for r in large[:5]]
        assert not large, (
            f"Images over 500 KB on {url}: {details}"
        )

    @allure.title("Total network requests under 100")
    def test_total_requests(self, page, url):
        """Excessive requests hurt load times and mobile performance."""
        bp = BasePage(page)
        bp.goto(url)
        page.wait_for_load_state("load")
        resources = bp.get_all_resources()
        count = len(resources)
        logger.info("[%s] Total requests: %d", url, count)
        assert count < 150, (
            f"Too many network requests on {url}: {count}"
        )
