"""Einfache Kalenderoberfläche mit Konfliktbehandlung."""

from __future__ import annotations

import logging

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - z. B. in Testumgebungen
    tk = None  # type: ignore
    messagebox = None  # type: ignore

from start_cli import _load_groups, sync_caldav, close

logger = logging.getLogger(__name__)


def refresh_display(listbox: tk.Listbox, group_var: tk.StringVar) -> None:
    """Anzeige der Termine aktualisieren."""
    groups, _ = _load_groups()
    events = groups.get(group_var.get(), [])
    listbox.delete(0, tk.END)
    for ev in events:
        txt = f"{ev['date']}: {ev['title']}"
        if ev.get("alarm"):
            txt += f" (Alarm {ev['alarm']} min)"
        listbox.insert(tk.END, txt)


def sync_cb(group_var: tk.StringVar) -> None:
    """CalDAV-Synchronisation starten."""
    try:
        sync_caldav("http://example.com/cal", group=group_var.get())
    except Exception as exc:  # pragma: no cover - Netzwerkfehler
        logger.error("Synchronisation fehlgeschlagen: %s", exc)


def run() -> None:
    """GUI starten."""
    if tk is None:
        logger.error("tkinter nicht verfügbar")
        return
    root = tk.Tk()
    root.title("Kalender")
    group_var = tk.StringVar(value="default")

    tk.Label(root, text="Gruppe").grid(row=0, column=0)
    tk.Entry(root, textvariable=group_var).grid(row=0, column=1)

    listbox = tk.Listbox(root, width=40)
    listbox.grid(row=1, column=0, columnspan=2, pady=5)

    tk.Button(root, text="Synchronisieren", command=lambda: sync_cb(group_var)).grid(
        row=2, column=0, columnspan=2
    )
    refresh_display(listbox, group_var)

    root.mainloop()
    close()


__all__ = ["run", "sync_cb", "refresh_display"]
