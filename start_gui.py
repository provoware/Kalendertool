"""Autonomes Startskript für die GUI mit Abhängigkeitsprüfung."""

from __future__ import annotations

import shutil
import subprocess
import sys
import logging

from videobatch_launcher import bootstrap_console
from logging_config import setup_logging

logger = logging.getLogger(__name__)


def _ensure_ffmpeg() -> None:
    """Installiere ffmpeg bei Bedarf automatisch."""
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        logger.info("FFmpeg gefunden")
        return
    if sys.platform.startswith("linux") and shutil.which("apt"):
        try:
            subprocess.check_call(
                ["sudo", "apt", "update"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.check_call(
                ["sudo", "apt", "install", "-y", "ffmpeg"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("FFmpeg erfolgreich installiert")
        except Exception as exc:  # pragma: no cover - Installation kann variieren
            logger.error("FFmpeg konnte nicht automatisch installiert werden: %s", exc)
    else:  # pragma: no cover - Plattformabhängig
        msg = "FFmpeg nicht gefunden. Bitte manuell installieren."
        if sys.platform.startswith("win"):
            msg += " Windows: 'winget install ffmpeg'"
        elif sys.platform == "darwin":
            msg += " macOS: 'brew install ffmpeg'"
        else:
            msg += " Siehe https://ffmpeg.org"
        logger.error(msg)
        logger.error(
            "FFmpeg nicht gefunden. Bitte manuell von https://ffmpeg.org installieren."
        )


def main() -> None:
    """Start the tool after an automatic check."""
    setup_logging()
    bootstrap_console()
    _ensure_ffmpeg()
    try:
        import videobatch_gui as gui  # Import nach Prüfung

        gui.run_gui()
    except Exception as exc:  # pragma: no cover - GUI-Fehler schwer testbar
        logger.error("GUI konnte nicht gestartet werden: %s", exc)


if __name__ == "__main__":
    main()
