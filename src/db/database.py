import sqlite3
import json
from datetime import datetime
from pathlib import Path

_DB_PATH = Path(__file__).parent.parent.parent / "reports.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                checked_at TEXT NOT NULL,
                total_checks INTEGER,
                passed INTEGER,
                failed INTEGER,
                not_applicable INTEGER,
                results_json TEXT NOT NULL
            )
        """)


def save_report(filename: str, file_type: str, results: list[dict]) -> int:
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    na = sum(1 for r in results if r["status"] == "na")
    with _get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO reports
               (filename, file_type, checked_at, total_checks, passed, failed, not_applicable, results_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (filename, file_type, datetime.utcnow().isoformat(), len(results),
             passed, failed, na, json.dumps(results)),
        )
        return cursor.lastrowid


def get_all_reports() -> list[dict]:
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT id, filename, file_type, checked_at, total_checks, passed, failed, not_applicable "
            "FROM reports ORDER BY checked_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_report_by_id(report_id: int) -> "dict | None":
    with _get_connection() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["results"] = json.loads(data.pop("results_json"))
    return data
