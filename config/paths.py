"""Zentrale Pfade und Dateien."""

from pathlib import Path
from datetime import datetime

BASE_DIR = Path.home() / ".videobatchtool"
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"
ARCHIVE_DIR = BASE_DIR / "archive"

# Dateien
NOTES_FILE = BASE_DIR / "notes.txt"
LOG_FILE = LOG_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"

for d in (DATA_DIR, CONFIG_DIR, LOG_DIR, ARCHIVE_DIR):
    d.mkdir(parents=True, exist_ok=True)
