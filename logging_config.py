"""Zentrale Konfiguration für das Logging."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_file: Path | str = "kalendertool.log") -> None:
    """Richte Logging für Datei und Konsole ein."""
    log_path = Path(log_file)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )
