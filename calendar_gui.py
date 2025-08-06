"""Einfache Kalenderoberfläche mit Konfliktbehandlung."""

from __future__ import annotations

import logging

try:  # tkinter kann in Testumgebungen fehlen
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - Fallback, falls tkinter fehlt
    tk = None  # type: ignore
    messagebox = None  # type: ignore

import sync_caldav

logger = logging.getLogger(__name__)


def sync_cb() -> None:
    """CalDAV synchronisieren und Konflikte auflösen."""

    conflicts = sync_caldav.sync_caldav()
    if not conflicts:
        refresh_display()
        return

    if tk is None or messagebox is None:
        logger.warning(
            "tkinter nicht verfügbar; Konflikte können nicht angezeigt werden"
        )
        return

    try:
        root = tk.Tk()
        root.withdraw()
    except Exception:  # pragma: no cover - GUI-Fehler im Test
        logger.exception("Tk-Initialisierung fehlgeschlagen")
        return

    for conflict in conflicts:
        summary = conflict.get("summary", "Unbekannt")
        local = conflict.get("local", "")
        server = conflict.get("server", "")
        msg = (
            f"Konflikt für {summary}\n\n"
            f"Lokal: {local}\nServer: {server}\n\n"
            "Lokale Version behalten?"
        )
        keep_local = messagebox.askyesno("Kalenderkonflikt", msg)
        chosen = local if keep_local else server
        sync_caldav.apply_choice(conflict, chosen)

    root.destroy()
    refresh_display()


def refresh_display() -> None:
    """Kalenderanzeige aktualisieren."""

    logger.info("Kalenderanzeige aktualisiert")
