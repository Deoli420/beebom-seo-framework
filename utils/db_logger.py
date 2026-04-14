"""
SQLite database logger for Beebom SEO test results.

Stores run summaries and individual test results so that
trend analysis and regression detection can be performed.
"""

from __future__ import annotations

import sqlite3
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "results.db"


def _connect() -> sqlite3.Connection:
    """Return a connection to the results SQLite database."""
    return sqlite3.connect(str(DB_PATH))


def create_tables() -> None:
    """Create the test_runs and test_results tables if they do not exist."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_runs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date    TEXT    NOT NULL,
            total_tests INTEGER NOT NULL,
            passed      INTEGER NOT NULL,
            failed      INTEGER NOT NULL,
            duration    REAL    NOT NULL DEFAULT 0.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id    INTEGER NOT NULL,
            url       TEXT    NOT NULL DEFAULT '',
            test_name TEXT    NOT NULL,
            status    TEXT    NOT NULL,
            error_msg TEXT    NOT NULL DEFAULT '',
            timestamp TEXT    NOT NULL,
            FOREIGN KEY (run_id) REFERENCES test_runs(id)
        )
    """)
    conn.commit()
    conn.close()
    logger.info("DB tables ensured at %s", DB_PATH)


def log_run(total: int, passed: int, failed: int, duration: float) -> int:
    """Insert a test-run summary row and return its id.

    Args:
        total: Total number of tests executed.
        passed: Number of passing tests.
        failed: Number of failing tests.
        duration: Total run duration in seconds.

    Returns:
        The auto-incremented run id.
    """
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_runs (run_date, total_tests, passed, failed, duration) "
        "VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), total, passed, failed, duration),
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info("Logged run #%d — total=%d passed=%d failed=%d", run_id, total, passed, failed)
    return run_id


def log_result(run_id: int, url: str, test_name: str, status: str, error_msg: str = "") -> None:
    """Insert an individual test result row.

    Args:
        run_id: The parent test_runs.id.
        url: The URL under test (may be empty).
        test_name: Fully-qualified test node id.
        status: 'passed' or 'failed'.
        error_msg: Error traceback snippet for failures.
    """
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_results (run_id, url, test_name, status, error_msg, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (run_id, url, test_name, status, error_msg, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_last_5_runs() -> list[dict]:
    """Return the 5 most recent run summaries, newest first."""
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM test_runs ORDER BY id DESC LIMIT 5"
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_failing_tests() -> list[dict]:
    """Return tests that failed in the most recent run."""
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT tr.* FROM test_results tr "
        "JOIN test_runs trn ON tr.run_id = trn.id "
        "WHERE tr.status = 'failed' "
        "ORDER BY trn.id DESC LIMIT 50"
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows
