from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from videobatch_extra import build_out_name, human_time  # noqa: E402
from videobatch_extra import cli_encode  # noqa: E402


def test_human_time_format():
    assert human_time(65) == "01:05"


def test_build_out_name(tmp_path):
    result = build_out_name(Path("song.mp3"), tmp_path)
    assert result.parent == Path(tmp_path)
    assert result.suffix == ".mp4"
    assert result.name.startswith("song_")


def test_cli_encode_exit_codes(tmp_path, monkeypatch):
    img = tmp_path / "img.jpg"
    img.write_bytes(b"")
    aud = tmp_path / "aud.mp3"
    aud.write_bytes(b"")
    monkeypatch.setattr("videobatch_extra.run_ffmpeg", lambda cmd: None)
    ok = cli_encode([img], [aud], tmp_path)
    assert ok == 0
    bad = cli_encode([img], [], tmp_path)
    assert bad == 1

    def fail(cmd):
        raise RuntimeError("fail")

    monkeypatch.setattr("videobatch_extra.run_ffmpeg", fail)
    err = cli_encode([img], [aud], tmp_path)
    assert err == 2
