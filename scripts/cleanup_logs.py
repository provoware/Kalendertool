"""Entferne alte Logdateien."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from config.paths import LOG_DIR


def cleanup_logs(log_dir: Path = LOG_DIR, days: int = 30) -> None:
    """Loesche Logdateien, die aelter als ``days`` Tage sind."""
    cutoff = datetime.now() - timedelta(days=days)
    for file in log_dir.glob("*.log*"):
        if datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
            file.unlink()


if __name__ == "__main__":
    cleanup_logs()
