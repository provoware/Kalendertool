"""Persistente Ablage mit SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict


def save_project(data: Dict[str, Any], db_path: Path) -> None:
    """Projekt in SQLite-Datenbank speichern."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS project (id INTEGER PRIMARY KEY, data TEXT)"
    )
    cur.execute("DELETE FROM project")
    cur.execute("INSERT INTO project (data) VALUES (?)", [json.dumps(data)])
    conn.commit()
    conn.close()


def load_project(db_path: Path) -> Dict[str, Any]:
    """Projekt aus SQLite-Datenbank laden."""
    if not db_path.exists():
        return {"pairs": [], "settings": {}}
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS project (id INTEGER PRIMARY KEY, data TEXT)"
    )
    cur.execute("SELECT data FROM project ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return {"pairs": [], "settings": {}}


__all__ = ["save_project", "load_project"]
