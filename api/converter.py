"""Hilfsfunktionen zum Erstellen von Videos."""

from __future__ import annotations

import subprocess
from typing import List


def build_ffmpeg_cmd(
    image_path: str,
    audio_path: str,
    output: str,
    width: int,
    height: int,
    abitrate: str,
    crf: int,
    preset: str,
) -> List[str]:
    """Erzeuge den ffmpeg-Aufruf.

    Parameters
    ----------
    image_path: str
        Pfad zum Bild.
    audio_path: str
        Pfad zur Audiodatei.
    output: str
        Zielvideodatei.
    width: int
        Zielbreite.
    height: int
        Zielhöhe.
    abitrate: str
        Audio-Bitrate, z.B. ``"192k"``.
    crf: int
        Qualitätsfaktor ("Constant Rate Factor").
    preset: str
        ffmpeg-Voreinstellung für Geschwindigkeit/Qualität.
    """
    return [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
        "-i",
        audio_path,
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-vf",
        (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        ),
        "-c:a",
        "aac",
        "-b:a",
        abitrate,
        "-shortest",
        "-preset",
        preset,
        "-crf",
        str(crf),
        output,
    ]


def run_ffmpeg(cmd: List[str]) -> subprocess.Popen:
    """Starte ffmpeg mit dem gegebenen Befehl."""
    return subprocess.Popen(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
