"""
Pytest configuration and shared fixtures for Beebom SEO tests.

Uses pytest-playwright's built-in browser management and adds
mobile viewport, screenshot-on-failure, and DB logging.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv

from pages.base_page import BasePage
from utils.db_logger import create_tables, log_run, log_result

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://beebom.com")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# Initialise DB tables once per process.
create_tables()


# ---------------------------------------------------------------------------
# Playwright config (pytest-playwright hooks)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Override default Playwright launch args."""
    return {"headless": HEADLESS}


@pytest.fixture(scope="session")
def browser_context_args():
    """Default browser context args — desktop viewport."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }


# ---------------------------------------------------------------------------
# Custom fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mobile_page(browser):
    """Create a page inside a mobile browser context (iPhone 13)."""
    ctx = browser.new_context(
        viewport={"width": 390, "height": 844},
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/16.0 Mobile/15E148 Safari/604.1"
        ),
        is_mobile=True,
        has_touch=True,
    )
    pg = ctx.new_page()
    yield pg
    pg.close()
    ctx.close()


@pytest.fixture
def target_url():
    """Return the BASE_URL read from .env or default."""
    return BASE_URL


# ---------------------------------------------------------------------------
# Hooks — screenshot on failure & DB logging
# ---------------------------------------------------------------------------

# Session-level accumulators for the run summary.
_results: list[dict] = []


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on test failure and collect per-test results."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        status = "passed" if report.passed else "failed"
        error_msg = str(report.longrepr)[:500] if report.failed else ""

        # Extract the URL parameter if present.
        url = ""
        if hasattr(item, "callspec") and "url" in item.callspec.params:
            url = item.callspec.params["url"]

        _results.append(
            {
                "url": url,
                "test_name": item.nodeid,
                "status": status,
                "error_msg": error_msg,
            }
        )

        # Screenshot on failure.
        if report.failed:
            page_fixture = item.funcargs.get("page") or item.funcargs.get("mobile_page")
            if page_fixture:
                screenshot_name = f"{item.nodeid.replace('/', '_').replace('::', '_')}.png"
                screenshot_path = SCREENSHOT_DIR / screenshot_name
                try:
                    page_fixture.screenshot(path=str(screenshot_path))
                    allure.attach.file(
                        str(screenshot_path),
                        name="failure-screenshot",
                        attachment_type=allure.attachment_type.PNG,
                    )
                    logger.info("Screenshot saved: %s", screenshot_path)
                except Exception as exc:
                    logger.warning("Could not capture screenshot: %s", exc)


def pytest_sessionfinish(session, exitstatus):
    """Log the full run summary and per-test results to SQLite."""
    if not _results:
        return

    passed = sum(1 for r in _results if r["status"] == "passed")
    failed = sum(1 for r in _results if r["status"] == "failed")
    total = len(_results)
    duration = 0.0

    run_id = log_run(total, passed, failed, duration)
    for r in _results:
        log_result(run_id, r["url"], r["test_name"], r["status"], r["error_msg"])

    logger.info(
        "Run #%d logged — total=%d  passed=%d  failed=%d",
        run_id, total, passed, failed,
    )
