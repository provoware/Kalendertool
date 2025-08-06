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


def start_ffmpeg(cmd: List[str]) -> subprocess.Popen:
    """Starte ffmpeg asynchron (im Hintergrund)."""
    return subprocess.Popen(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )


def run_ffmpeg(cmd: List[str]) -> subprocess.CompletedProcess:
    """Führe ffmpeg aus und werte den Rückgabecode aus.

    Gibt ein ``CompletedProcess``-Objekt zurück oder hebt bei Fehlern eine
    ``RuntimeError`` mit der letzten Fehlermeldung (``stderr``) aus.
    """
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    if res.returncode != 0:
        msg = res.stderr.strip() or f"ffmpeg Fehlercode {res.returncode}"
        raise RuntimeError(msg)
    return res
