"""Zentrale Pfade und Dateien."""

from pathlib import Path
from datetime import datetime
from typing import Iterable

BASE_DIR = Path.home() / ".videobatchtool"
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"
ARCHIVE_DIR = BASE_DIR / "archive"
HELP_DIR = BASE_DIR / "help"
USED_DIR = Path.home() / "benutzte_dateien"
DEFAULT_OUT_DIR = Path.home() / "Videos" / "VideoBatchTool_Out"

# Dateien
NOTES_FILE = BASE_DIR / "notes.txt"
LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
PROJECT_DB = DATA_DIR / "autosave.db"

_DIRS: tuple[Path, ...] = (
    DATA_DIR,
    CONFIG_DIR,
    LOG_DIR,
    ARCHIVE_DIR,
    HELP_DIR,
    USED_DIR,
    DEFAULT_OUT_DIR,
)


def ensure_directories(dirs: Iterable[Path] = _DIRS) -> None:
    """Benötigte Ordner anlegen (Directory Creation)."""
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "CONFIG_DIR",
    "LOG_DIR",
    "ARCHIVE_DIR",
    "HELP_DIR",
    "USED_DIR",
    "DEFAULT_OUT_DIR",
    "NOTES_FILE",
    "LOG_FILE",
    "PROJECT_DB",
    "ensure_directories",
]
