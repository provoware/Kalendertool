"""Stub-Modul für CalDAV-Synchronisation."""

from __future__ import annotations

from typing import Any, Dict, List


def sync_caldav() -> List[Dict[str, Any]]:
    """Mit einem CalDAV-Server abgleichen.

    Returns:
        Liste von Konflikten, jeweils mit ``summary``, ``local`` und ``server``.
    """

    return []


def apply_choice(conflict: Dict[str, Any], chosen: Any) -> None:
    """Ausgewählte Version eines Konflikts anwenden."""

    _ = conflict
    _ = chosen
