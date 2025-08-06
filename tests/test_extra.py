from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from videobatch_extra import build_out_name, human_time  # noqa: E402


def test_human_time_format():
    assert human_time(65) == "01:05"


def test_build_out_name(tmp_path):
    result = build_out_name(Path("song.mp3"), tmp_path)
    assert result.parent == Path(tmp_path)
    assert result.suffix == ".mp4"
    assert result.name.startswith("song_")
