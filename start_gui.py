"""Autonomes Startskript für die GUI mit Abhängigkeitsprüfung."""

from __future__ import annotations

import shutil
import subprocess
import sys

from videobatch_launcher import bootstrap_console


def _ensure_ffmpeg() -> None:
    """Installiere ffmpeg bei Bedarf automatisch."""
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return
    if sys.platform.startswith("linux"):
        try:
            subprocess.check_call(["sudo", "apt", "update"], stdout=subprocess.DEVNULL)
            subprocess.check_call(
                ["sudo", "apt", "install", "-y", "ffmpeg"], stdout=subprocess.DEVNULL
            )
        except Exception as exc:  # pragma: no cover - Installation kann variieren
            print(f"FFmpeg konnte nicht automatisch installiert werden: {exc}")


def main() -> None:
    """Starte das Tool nach automatischer Prüfung."""
    bootstrap_console()
    _ensure_ffmpeg()
    import videobatch_gui as gui  # Import nach Prüfung

    gui.run_gui()


if __name__ == "__main__":
    main()
