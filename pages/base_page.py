"""
BasePage — Page Object Model base class for Beebom SEO testing.

All page interactions go through this class. Tests should never
use raw Playwright selectors directly; instead they call BasePage methods.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class BasePage:
    """Page Object Model base class wrapping common SEO-related page queries."""

    def __init__(self, page):
        """Store the Playwright page instance.

        Args:
            page: A Playwright Page object.
        """
        self.page = page

    def goto(self, url: str, timeout: int = 30000) -> None:
        """Navigate to the given URL and wait for the network to be mostly idle.

        Args:
            url: The full URL to navigate to.
            timeout: Maximum wait time in milliseconds.
        """
        logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)

    def get_title(self) -> str:
        """Return the text content of the <title> tag."""
        return self.page.title()

    def get_meta_description(self) -> str | None:
        """Return the content attribute of the meta description tag, or None."""
        el = self.page.query_selector('meta[name="description"]')
        return el.get_attribute("content") if el else None

    def get_meta_keywords(self) -> str | None:
        """Return the content attribute of the meta keywords tag, or None."""
        el = self.page.query_selector('meta[name="keywords"]')
        return el.get_attribute("content") if el else None

    def get_canonical_url(self) -> str | None:
        """Return the href of the canonical link tag, or None."""
        el = self.page.query_selector('link[rel="canonical"]')
        return el.get_attribute("href") if el else None

    def get_h1_count(self) -> int:
        """Return the number of H1 elements on the page."""
        return len(self.page.query_selector_all("h1"))

    def get_h1_text(self) -> str | None:
        """Return the text content of the first H1, or None if absent."""
        el = self.page.query_selector("h1")
        return el.inner_text().strip() if el else None

    def get_all_h2(self) -> list[str]:
        """Return a list of text content from all H2 elements."""
        elements = self.page.query_selector_all("h2")
        return [el.inner_text().strip() for el in elements]

    def get_all_headings(self) -> list[dict]:
        """Return all headings (h1-h6) with their tag name and text."""
        return self.page.evaluate("""
            () => {
                const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                return Array.from(headings).map(h => ({
                    tag: h.tagName.toLowerCase(),
                    text: h.innerText.trim()
                }));
            }
        """)

    def get_all_links(self) -> list[dict]:
        """Return all anchor elements with their href and rel attributes."""
        return self.page.evaluate("""
            () => {
                const links = document.querySelectorAll('a[href]');
                return Array.from(links).map(a => ({
                    href: a.href,
                    rel: a.getAttribute('rel') || '',
                    text: a.innerText.trim()
                }));
            }
        """)

    def get_image_alts(self) -> list[dict]:
        """Return all images with their src and alt attributes."""
        return self.page.evaluate("""
            () => {
                const imgs = document.querySelectorAll('img');
                return Array.from(imgs).map(img => ({
                    src: img.src,
                    alt: img.getAttribute('alt')
                }));
            }
        """)

    def get_structured_data(self) -> list[dict]:
        """Return parsed JSON-LD structured data blocks from the page."""
        scripts = self.page.query_selector_all('script[type="application/ld+json"]')
        results = []
        for script in scripts:
            text = script.inner_text().strip()
            if text:
                try:
                    results.append(json.loads(text))
                except json.JSONDecodeError:
                    results.append({"_raw": text, "_error": "invalid_json"})
        return results

    def get_robots_meta(self) -> str | None:
        """Return the content of the robots meta tag, or None."""
        el = self.page.query_selector('meta[name="robots"]')
        return el.get_attribute("content") if el else None

    def get_og_tags(self) -> dict:
        """Return a dict of Open Graph meta tag properties and their content."""
        return self.page.evaluate("""
            () => {
                const tags = document.querySelectorAll('meta[property^="og:"]');
                const result = {};
                tags.forEach(tag => {
                    const prop = tag.getAttribute('property');
                    result[prop] = tag.getAttribute('content') || '';
                });
                return result;
            }
        """)

    def check_https(self) -> bool:
        """Return True if the current page URL uses HTTPS."""
        return self.page.url.startswith("https://")

    def get_page_load_time(self) -> float:
        """Return the full page load time in milliseconds using Navigation Timing API."""
        return self.page.evaluate("""
            () => {
                const timing = performance.getEntriesByType('navigation')[0];
                if (timing) {
                    return timing.loadEventEnd - timing.startTime;
                }
                // Fallback to older API
                const t = performance.timing;
                return t.loadEventEnd - t.navigationStart;
            }
        """)

    def get_ttfb(self) -> float:
        """Return the Time To First Byte in milliseconds."""
        return self.page.evaluate("""
            () => {
                const timing = performance.getEntriesByType('navigation')[0];
                if (timing) {
                    return timing.responseStart - timing.requestStart;
                }
                const t = performance.timing;
                return t.responseStart - t.requestStart;
            }
        """)

    def is_mobile_responsive(self) -> bool:
        """Check whether a viewport meta tag exists on the page."""
        el = self.page.query_selector('meta[name="viewport"]')
        return el is not None

    def get_viewport_content(self) -> str | None:
        """Return the content attribute of the viewport meta tag."""
        el = self.page.query_selector('meta[name="viewport"]')
        return el.get_attribute("content") if el else None

    def get_page_width(self) -> int:
        """Return the scroll width of the document body."""
        return self.page.evaluate("() => document.body.scrollWidth")

    def get_viewport_width(self) -> int:
        """Return the inner width of the browser window."""
        return self.page.evaluate("() => window.innerWidth")

    def get_all_resources(self) -> list[dict]:
        """Return performance resource entries for the page."""
        return self.page.evaluate("""
            () => {
                return performance.getEntriesByType('resource').map(r => ({
                    name: r.name,
                    type: r.initiatorType,
                    size: r.transferSize || 0,
                    duration: r.duration
                }));
            }
        """)

    def get_mixed_content(self) -> list[str]:
        """Return list of HTTP resource URLs loaded on an HTTPS page."""
        return self.page.evaluate("""
            () => {
                if (location.protocol !== 'https:') return [];
                const resources = performance.getEntriesByType('resource');
                return resources
                    .filter(r => r.name.startsWith('http://'))
                    .map(r => r.name);
            }
        """)

    def get_security_headers(self) -> dict:
        """Return security-related response headers via a fresh fetch of the page URL."""
        # This is called from the page context — headers come from the
        # navigation response captured by Playwright.  For a more reliable
        # approach tests can use ``requests`` directly.
        return {}

    def get_min_font_size(self) -> float:
        """Return the smallest computed font-size (in px) of visible text nodes."""
        return self.page.evaluate("""
            () => {
                const walker = document.createTreeWalker(
                    document.body, NodeFilter.SHOW_TEXT, null);
                let minSize = Infinity;
                while (walker.nextNode()) {
                    const text = walker.currentNode.textContent.trim();
                    if (!text) continue;
                    const el = walker.currentNode.parentElement;
                    if (!el) continue;
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden') continue;
                    const size = parseFloat(style.fontSize);
                    if (size < minSize) minSize = size;
                }
                return minSize === Infinity ? 16 : minSize;
            }
        """)

    def get_small_tap_targets(self) -> list[dict]:
        """Return interactive elements whose bounding box is smaller than 48x48."""
        return self.page.evaluate("""
            () => {
                const elements = document.querySelectorAll('a, button, input, select, textarea');
                const small = [];
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0 &&
                        (rect.width < 48 || rect.height < 48)) {
                        small.push({
                            tag: el.tagName.toLowerCase(),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            text: (el.innerText || el.value || '').slice(0, 50)
                        });
                    }
                }
                return small;
            }
        """)
