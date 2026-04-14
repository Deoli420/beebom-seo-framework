"""
Security and technical SEO tests for Beebom.

Validates HTTPS enforcement, mixed-content issues, robots.txt,
sitemap.xml, and security headers.
"""

import logging
from xml.etree import ElementTree

import allure
import pytest
import requests

from pages.base_page import BasePage
from data.urls import SMOKE_URLS

logger = logging.getLogger(__name__)

BASE = "https://beebom.com"


@pytest.mark.security
@pytest.mark.parametrize("url", SMOKE_URLS)
class TestSecurity:
    """HTTPS and mixed-content checks for selected pages."""

    @allure.title("Page is served over HTTPS")
    def test_https_enabled(self, page, url):
        """All public pages must use HTTPS for security and SEO ranking."""
        bp = BasePage(page)
        bp.goto(url)
        assert bp.check_https(), f"Page not HTTPS: {url}"

    @allure.title("No mixed content (HTTP resources on HTTPS page)")
    def test_no_mixed_content(self, page, url):
        """HTTP sub-resources on HTTPS pages trigger browser warnings."""
        bp = BasePage(page)
        bp.goto(url)
        page.wait_for_load_state("load")
        mixed = bp.get_mixed_content()
        logger.info("[%s] Mixed-content resources: %d", url, len(mixed))
        assert not mixed, (
            f"Mixed content on {url}: {mixed[:5]}"
        )


@pytest.mark.security
class TestSitewideSecurity:
    """One-off site-level checks (not parametrized per URL)."""

    @allure.title("HTTP redirects to HTTPS")
    def test_www_redirects(self):
        """http://beebom.com must 301-redirect to https://."""
        resp = requests.get("http://beebom.com", timeout=15, allow_redirects=False)
        logger.info("HTTP redirect status: %d, Location: %s",
                     resp.status_code, resp.headers.get("Location", ""))
        assert resp.status_code in (301, 302, 307, 308), (
            f"HTTP does not redirect: status {resp.status_code}"
        )
        location = resp.headers.get("Location", "")
        assert location.startswith("https://"), (
            f"Redirect target is not HTTPS: {location}"
        )

    @allure.title("robots.txt is accessible")
    def test_robots_txt_accessible(self):
        """/robots.txt must return HTTP 200."""
        resp = requests.get(f"{BASE}/robots.txt", timeout=10)
        logger.info("robots.txt status: %d", resp.status_code)
        assert resp.status_code == 200, (
            f"robots.txt returned {resp.status_code}"
        )

    @allure.title("sitemap.xml is accessible")
    def test_sitemap_accessible(self):
        """/sitemap.xml must return HTTP 200."""
        resp = requests.get(f"{BASE}/sitemap.xml", timeout=10)
        logger.info("sitemap.xml status: %d", resp.status_code)
        assert resp.status_code == 200, (
            f"sitemap.xml returned {resp.status_code}"
        )

    @allure.title("sitemap.xml is valid XML")
    def test_sitemap_valid_xml(self):
        """The sitemap must be parseable as well-formed XML."""
        resp = requests.get(f"{BASE}/sitemap.xml", timeout=10)
        if resp.status_code != 200:
            pytest.skip("Sitemap not accessible")
        try:
            ElementTree.fromstring(resp.content)
        except ElementTree.ParseError as exc:
            pytest.fail(f"sitemap.xml is not valid XML: {exc}")

    @allure.title("X-Frame-Options header present")
    def test_x_frame_options(self):
        """X-Frame-Options (or CSP frame-ancestors) prevents clickjacking."""
        resp = requests.get(BASE, timeout=10)
        xfo = resp.headers.get("X-Frame-Options", "")
        csp = resp.headers.get("Content-Security-Policy", "")
        has_protection = bool(xfo) or "frame-ancestors" in csp
        logger.info("X-Frame-Options: %s, CSP frame-ancestors: %s",
                     xfo or "(none)", "present" if "frame-ancestors" in csp else "(none)")
        assert has_protection, "No clickjacking protection header found"
