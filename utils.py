"""Gemeinsame Hilfsfunktionen."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


def human_time(sec: int) -> str:
    """Sekunden als HH:MM:SS oder MM:SS formatieren."""
    sec = int(sec)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def build_out_name(audio: Path | str, out_dir: Path) -> Path:
    """Ausgabedatei aus Audiopfad und Zeitstempel ableiten."""
    audio = Path(audio)
    return out_dir / f"{audio.stem}_{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"


__all__ = ["human_time", "build_out_name"]
