from pathlib import Path
import sys

import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))

from start_cli import add_event, export_ical, sync_caldav, close  # noqa: E402


def test_export_creates_file(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("start_cli.DB_PATH", tmp_path / "events.db")
    close()
    add_event("Feier", "2025-12-24", alarm=30)
    out = tmp_path / "events.ics"
    export_ical(out)
    content = out.read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in content
    assert "SUMMARY:Feier" in content
    assert "BEGIN:VALARM" in content
    assert "TRIGGER:-PT30M" in content


def test_group_specific_export(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("start_cli.DB_PATH", tmp_path / "events.db")
    close()
    add_event("Familie", "2025-12-24", group="familie")
    out = tmp_path / "familie.ics"
    export_ical(out, group="familie")
    content = out.read_text(encoding="utf-8")
    assert "SUMMARY:Familie" in content


def test_export_requires_force(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("start_cli.DB_PATH", tmp_path / "events.db")
    close()
    add_event("Alt", "2025-12-24")
    out = tmp_path / "events.ics"
    export_ical(out)
    add_event("Neu", "2025-12-25")
    with caplog.at_level("ERROR"):
        export_ical(out)
    assert "existiert bereits" in caplog.text
    export_ical(out, force=True)
    content = out.read_text(encoding="utf-8")
    assert "SUMMARY:Neu" in content


def test_sync_caldav_calls_put(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("start_cli.DB_PATH", tmp_path / "events.db")
    close()
    add_event("Meeting", "2025-01-01", group="team")

    calls = {}

    def fake_put(
        url, data, headers, auth, timeout
    ):  # pragma: no cover - einfacher Mock
        calls["url"] = url
        return type("R", (), {"status_code": 200})()

    monkeypatch.setattr("requests.put", fake_put)
    sync_caldav("http://example.com/cal", "user", "pass", "team")
    assert calls["url"] == "http://example.com/cal"


def test_sync_caldav_retries_on_error(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("start_cli.DB_PATH", tmp_path / "events.db")
    close()
    add_event("Meeting", "2025-01-01", group="team")

    calls = {"count": 0}

    def fake_put(
        url, data, headers, auth, timeout
    ):  # pragma: no cover - einfacher Mock
        calls["count"] += 1
        raise requests.RequestException("netzwerk")

    monkeypatch.setattr("requests.put", fake_put)
    sync_caldav("http://example.com/cal", "user", "pass", "team")
    assert calls["count"] == 3
