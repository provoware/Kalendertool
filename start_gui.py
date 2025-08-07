"""Startet die Kalender-GUI."""

from __future__ import annotations

import logging

from logging_config import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the calendar GUI with logging."""
    setup_logging()
    try:
        from calendar_gui import run

        run()
    except Exception as exc:  # pragma: no cover - GUI-Fehler schwer testbar
        logger.error("GUI konnte nicht gestartet werden: %s", exc)


if __name__ == "__main__":
    main()
