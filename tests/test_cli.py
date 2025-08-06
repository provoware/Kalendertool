from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from start_cli import add_event, export_ical  # noqa: E402


def test_export_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("start_cli.DB_PATH", tmp_path / "events.db")
    add_event("Feier", "2025-12-24")
    out = tmp_path / "events.ics"
    export_ical(out)
    content = out.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in content
    assert "SUMMARY:Feier" in content
