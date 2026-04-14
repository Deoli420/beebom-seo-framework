"""
Structured data / Schema.org tests for Beebom.

Validates JSON-LD presence, validity, and correct schema types
for articles, the homepage, and category pages.
"""

import json
import logging

import allure
import pytest

from pages.base_page import BasePage
from data.urls import ALL_URLS, HOMEPAGE, CATEGORY_URLS, ARTICLE_URLS

logger = logging.getLogger(__name__)


@pytest.mark.regression
@pytest.mark.parametrize("url", ALL_URLS)
class TestStructuredData:
    """Schema markup checks for different page types."""

    @allure.title("JSON-LD script tag exists")
    def test_json_ld_exists(self, page, url):
        """Pages should include at least one JSON-LD block for rich results."""
        bp = BasePage(page)
        bp.goto(url)
        data = bp.get_structured_data()
        logger.info("[%s] JSON-LD blocks: %d", url, len(data))
        assert len(data) >= 1, f"No JSON-LD structured data on {url}"

    @allure.title("JSON-LD is valid JSON")
    def test_json_ld_valid_json(self, page, url):
        """Every JSON-LD block must be parseable JSON."""
        bp = BasePage(page)
        bp.goto(url)
        data = bp.get_structured_data()
        invalid = [d for d in data if "_error" in d]
        assert not invalid, (
            f"Invalid JSON-LD on {url}: {[d.get('_raw', '')[:100] for d in invalid]}"
        )


@pytest.mark.regression
@pytest.mark.parametrize("url", ARTICLE_URLS)
class TestArticleSchema:
    """Article-specific schema checks."""

    @allure.title("Article pages have Article schema type")
    def test_article_schema(self, page, url):
        """Article pages should declare @type Article (or NewsArticle, etc.)."""
        bp = BasePage(page)
        bp.goto(url)
        data = bp.get_structured_data()
        article_types = {"Article", "NewsArticle", "BlogPosting", "TechArticle"}
        found = False
        for block in data:
            schema_type = block.get("@type", "")
            if isinstance(schema_type, list):
                if any(t in article_types for t in schema_type):
                    found = True
                    break
            elif schema_type in article_types:
                found = True
                break
            # Check @graph arrays.
            graph = block.get("@graph", [])
            for item in graph:
                t = item.get("@type", "")
                if isinstance(t, list):
                    if any(x in article_types for x in t):
                        found = True
                        break
                elif t in article_types:
                    found = True
                    break
        logger.info("[%s] Article schema found: %s", url, found)
        assert found, f"No Article schema type on {url}"


class TestHomepageSchema:
    """Homepage-specific schema checks."""

    @allure.title("Homepage has Organization schema")
    def test_organization_schema(self, page):
        """The homepage should include an Organization schema for brand identity."""
        bp = BasePage(page)
        bp.goto(HOMEPAGE)
        data = bp.get_structured_data()
        found = False
        for block in data:
            if block.get("@type") == "Organization":
                found = True
                break
            for item in block.get("@graph", []):
                if item.get("@type") == "Organization":
                    found = True
                    break
        logger.info("[%s] Organization schema: %s", HOMEPAGE, found)
        assert found, f"No Organization schema on {HOMEPAGE}"


@pytest.mark.regression
@pytest.mark.parametrize("url", CATEGORY_URLS)
class TestBreadcrumbSchema:
    """Category-page breadcrumb checks."""

    @allure.title("Category pages have BreadcrumbList schema")
    def test_breadcrumb_schema(self, page, url):
        """Breadcrumb structured data helps search engines understand site hierarchy."""
        bp = BasePage(page)
        bp.goto(url)
        data = bp.get_structured_data()
        found = False
        for block in data:
            if block.get("@type") == "BreadcrumbList":
                found = True
                break
            for item in block.get("@graph", []):
                if item.get("@type") == "BreadcrumbList":
                    found = True
                    break
        logger.info("[%s] BreadcrumbList schema: %s", url, found)
        assert found, f"No BreadcrumbList schema on {url}"
