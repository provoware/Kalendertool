from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from api import run_ffmpeg  # noqa: E402
import pytest


def test_run_ffmpeg_success():
    res = run_ffmpeg(["python", "-c", "print('ok')"])
    assert res.stdout.strip() == "ok"


def test_run_ffmpeg_failure():
    with pytest.raises(RuntimeError):
        run_ffmpeg(["python", "-c", "import sys; sys.exit(1)"])
