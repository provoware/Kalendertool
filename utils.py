"""Gemeinsame Hilfsfunktionen."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil


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


def which(p: str) -> str | None:
    """Pfad zu ausführbarem Programm ermitteln."""
    return shutil.which(p)


def check_ffmpeg() -> bool:
    """Prüfen, ob ffmpeg und ffprobe verfügbar sind."""
    return bool(which("ffmpeg") and which("ffprobe"))


def normalize_bitrate(text: str) -> str:
    """Audio-Bitrate auf ein gültiges Format bringen."""
    text = text.strip().lower()
    if not text:
        return "192k"
    m = re.fullmatch(r"(\d+)([km]?)", text)
    if not m:
        return "192k"
    value, unit = m.groups()
    unit = unit or "k"
    return f"{value}{unit}"


__all__ = [
    "human_time",
    "build_out_name",
    "which",
    "check_ffmpeg",
    "normalize_bitrate",
]
