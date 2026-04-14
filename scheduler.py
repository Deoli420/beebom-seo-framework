"""
Nightly scheduler for Beebom SEO test suite.

Runs the full pytest suite every night at 11 PM IST (17:30 UTC),
then sends an HTML email report. Designed to run as a background process.

Usage:
    python scheduler.py
"""

import logging
import subprocess
import sys
import time
from datetime import datetime

import schedule
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("scheduler")


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------


def run_tests() -> None:
    """Execute the full test suite and send the email report."""
    logger.info("=== Starting nightly SEO test run ===")
    start = time.time()

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest", "tests/",
                "-v",
                "--tb=short",
                "--alluredir=reports/allure-results",
            ],
            capture_output=True,
            text=True,
            cwd=str(__import__("pathlib").Path(__file__).resolve().parent),
        )
        logger.info("pytest stdout:\n%s", result.stdout[-2000:] if result.stdout else "(empty)")
        if result.stderr:
            logger.warning("pytest stderr:\n%s", result.stderr[-1000:])
    except Exception as exc:
        logger.error("Failed to run pytest: %s", exc)
        return

    duration = time.time() - start
    logger.info("Test run completed in %.1f seconds", duration)

    # Parse quick totals from pytest output.
    total = passed = failed = 0
    for line in (result.stdout or "").splitlines():
        if "passed" in line or "failed" in line:
            import re
            m_passed = re.search(r"(\d+) passed", line)
            m_failed = re.search(r"(\d+) failed", line)
            if m_passed:
                passed = int(m_passed.group(1))
            if m_failed:
                failed = int(m_failed.group(1))
            total = passed + failed

    if total == 0:
        logger.warning("Could not parse test totals from pytest output")
        return

    # Send email.
    try:
        from utils.email_reporter import send_report
        send_report(total, passed, failed)
    except Exception as exc:
        logger.error("Email report failed: %s", exc)


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

# 11 PM IST = 17:30 UTC
schedule.every().day.at("17:30").do(run_tests)

logger.info("Scheduler started — next run at 17:30 UTC (11 PM IST)")

if __name__ == "__main__":
    # Optionally run immediately on startup with --now flag.
    if "--now" in sys.argv:
        run_tests()

    while True:
        schedule.run_pending()
        time.sleep(60)
