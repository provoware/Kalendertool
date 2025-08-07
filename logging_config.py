"""Zentrale Konfiguration für das Logging."""

from __future__ import annotations

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from config.paths import LOG_DIR


def setup_logging(log_file: Path | str = LOG_DIR / "kalendertool.log") -> None:
    """Richte Logging für Datei und Konsole ein."""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            TimedRotatingFileHandler(
                log_path,
                when="midnight",
                backupCount=7,
                encoding="utf-8",
            ),
        ],
    )
