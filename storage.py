"""Persistente Ablage mit SQLite."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Dict, Optional

_conn: Optional[sqlite3.Connection] = None
_cache: Optional[Dict[str, Any]] = None
_lock = threading.Lock()


def _get_conn(db_path: Path) -> sqlite3.Connection:
    """Get or create the SQLite connection (thread-safe)."""

    global _conn
    with _lock:
        if _conn is None:
            _conn = sqlite3.connect(db_path, check_same_thread=False)
            _conn.execute(
                "CREATE TABLE IF NOT EXISTS project (id INTEGER PRIMARY KEY, data TEXT)"
            )
    return _conn


def save_project(data: Dict[str, Any], db_path: Path) -> None:
    """Projekt in SQLite-Datenbank speichern (mit Transaktion und Cache)."""

    conn = _get_conn(db_path)
    try:
        with _lock, conn:
            conn.execute("DELETE FROM project")
            conn.execute("INSERT INTO project (data) VALUES (?)", [json.dumps(data)])
        global _cache
        _cache = data
    except sqlite3.Error as exc:
        raise RuntimeError("Projekt konnte nicht gespeichert werden") from exc


def load_project(db_path: Path) -> Dict[str, Any]:
    """Projekt aus SQLite-Datenbank laden (mit Cache)."""

    global _cache
    with _lock:
        if _cache is not None:
            return _cache
        conn = _get_conn(db_path)
        try:
            cur = conn.execute("SELECT data FROM project ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
        except sqlite3.Error as exc:
            raise RuntimeError("Projekt konnte nicht geladen werden") from exc
        if row:
            _cache = json.loads(row[0])
        else:
            _cache = {"pairs": [], "settings": {}}
        return _cache


def close() -> None:
    """Verbindung schließen und Cache leeren (thread-safe)."""

    global _conn, _cache
    with _lock:
        if _conn is not None:
            _conn.close()
            _conn = None
        _cache = None


__all__ = ["save_project", "load_project", "close"]
