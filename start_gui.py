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
        except Exception as exc:  # pragma: no cover - Installation kann variieren
            print(f"FFmpeg konnte nicht automatisch installiert werden: {exc}")
    else:  # pragma: no cover - Plattformabhängig
        print(
            "FFmpeg nicht gefunden. Bitte manuell von https://ffmpeg.org installieren."
        )


def main() -> None:
    """Starte das Tool nach automatischer Prüfung."""
    bootstrap_console()
    _ensure_ffmpeg()
    try:
        import videobatch_gui as gui  # Import nach Prüfung

        gui.run_gui()
    except Exception as exc:  # pragma: no cover - GUI-Fehler schwer testbar
        print(f"GUI konnte nicht gestartet werden: {exc}")


if __name__ == "__main__":
    main()
