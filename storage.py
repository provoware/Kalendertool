"""Persistente Ablage mit SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

_conn: Optional[sqlite3.Connection] = None
_cache: Optional[Dict[str, Any]] = None


def _get_conn(db_path: Path) -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(db_path)
        _conn.execute(
            "CREATE TABLE IF NOT EXISTS project (id INTEGER PRIMARY KEY, data TEXT)"
        )
    return _conn


def save_project(data: Dict[str, Any], db_path: Path) -> None:
    """Projekt in SQLite-Datenbank speichern (mit Transaktion und Cache)."""
    conn = _get_conn(db_path)
    with conn:
        conn.execute("DELETE FROM project")
        conn.execute("INSERT INTO project (data) VALUES (?)", [json.dumps(data)])
    global _cache
    _cache = data


def load_project(db_path: Path) -> Dict[str, Any]:
    """Projekt aus SQLite-Datenbank laden (mit Cache)."""
    global _cache
    if _cache is not None:
        return _cache
    conn = _get_conn(db_path)
    cur = conn.execute("SELECT data FROM project ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        _cache = json.loads(row[0])
    else:
        _cache = {"pairs": [], "settings": {}}
    return _cache


def close() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


__all__ = ["save_project", "load_project", "close"]
