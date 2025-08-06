from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from start_cli import add_event, export_ical, sync_caldav  # noqa: E402
from storage import load_project, close  # noqa: E402


def test_export_creates_file(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("start_cli.DB_PATH", tmp_path / "events.db")
    add_event("Feier", "2025-12-24", alarm=30)
    out = tmp_path / "events.ics"
    export_ical(out)
    content = out.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in content
    assert "SUMMARY:Feier" in content
    assert "BEGIN:VALARM" in content
    assert "TRIGGER:-PT30M" in content


def test_sync_conflict(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    db = tmp_path / "events.db"
    monkeypatch.setattr("start_cli.DB_PATH", db)
    monkeypatch.setattr("start_cli.uuid4", lambda: "uid1")
    close()
    add_event("Meeting", "2025-01-01")
    ics = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "BEGIN:VEVENT\n"
        "UID:uid1\n"
        "DTSTAMP:20300101T000000Z\n"
        "DTSTART;VALUE=DATE:20250101\n"
        "SUMMARY:Remote\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )

    class DummyResp:
        text = ics

        def raise_for_status(self):
            return None

    monkeypatch.setattr("requests.get", lambda url, timeout=5: DummyResp())
    conflicts = sync_caldav("http://example.com/cal")
    assert conflicts
    data = load_project(db)
    assert data["events"][0]["title"] == "Meeting"
