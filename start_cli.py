"""Einfache Kalender-CLI mit Speicher in SQLite."""

from __future__ import annotations

import argparse
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import requests
from icalendar import Calendar
from requests import RequestException

from storage import load_project, save_project, close
from config.paths import PROJECT_DB, ensure_directories
from logging_config import setup_logging

DB_PATH = PROJECT_DB
logger = logging.getLogger(__name__)


def _load_groups() -> tuple[dict[str, list[dict[str, str]]], dict]:
    """Gruppen und Rohdaten laden."""
    ensure_directories()
    data = load_project(DB_PATH)
    groups = data.setdefault("groups", {})
    default_list = groups.setdefault("default", data.get("events", []))
    data["events"] = default_list
    return groups, data


def add_event(
    title: str, date_str: str, alarm: int | None = None, group: str = "default"
) -> None:
    """Termin speichern."""
    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        logger.error("Ungültiges Datum. Bitte JJJJ-MM-TT verwenden.")
        return
    if alarm is not None and alarm < 0:
        logger.error("Alarm muss eine positive Zahl sein.")
        return
    groups, data = _load_groups()
    entry = {
        "uid": str(uuid4()),
        "title": title,
        "date": date.isoformat(),
        "dtstamp": datetime.now(UTC).isoformat(),
    }
    if alarm is not None:
        entry["alarm"] = alarm
    groups.setdefault(group, []).append(entry)
    save_project(data, DB_PATH)
    logger.info(
        "Termin '%s' am %s in Gruppe '%s' gespeichert", title, date.date(), group
    )


def export_ical(
    file_path: Path, group: str = "default", *, force: bool = False
) -> None:
    """Termine als iCal-Datei exportieren."""
    groups, _ = _load_groups()
    events = groups.get(group, [])
    if not events:
        logger.info("Keine Termine zum Export in Gruppe '%s'.", group)
        return
    if file_path.exists() and not force:
        logger.error(
            "Datei %s existiert bereits. --force zum Überschreiben nutzen.",
            file_path,
        )
        return
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Kalendertool//DE"]
    for ev in events:
        date = datetime.fromisoformat(ev["date"]).strftime("%Y%m%d")
        stamp = datetime.fromisoformat(ev["dtstamp"]).strftime("%Y%m%dT%H%M%SZ")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{ev['uid']}",
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{date}",
                f"SUMMARY:{ev['title']}",
            ]
        )
        if ev.get("alarm") is not None:
            lines.extend(
                [
                    "BEGIN:VALARM",
                    f"TRIGGER:-PT{ev['alarm']}M",
                    "ACTION:DISPLAY",
                    f"DESCRIPTION:{ev['title']}",
                    "END:VALARM",
                ]
            )
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    file_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("iCal-Datei nach %s exportiert", file_path)


def remove_event(index: int, group: str = "default") -> None:
    """Termin aus einer Gruppe löschen."""
    groups, data = _load_groups()
    events = groups.get(group, [])
    if 0 <= index < len(events):
        removed = events.pop(index)
        save_project(data, DB_PATH)
        logger.info("Termin '%s' entfernt", removed["title"])
    else:
        logger.error("Kein Termin an Position %s", index)


def edit_event(
    index: int,
    title: str | None = None,
    date_str: str | None = None,
    alarm: int | None = None,
    group: str = "default",
) -> None:
    """Termin bearbeiten."""
    groups, data = _load_groups()
    events = groups.get(group, [])
    if not (0 <= index < len(events)):
        logger.error("Kein Termin an Position %s", index)
        return
    ev = events[index]
    if title is not None:
        ev["title"] = title
    if date_str is not None:
        try:
            ev["date"] = datetime.fromisoformat(date_str).isoformat()
        except ValueError:
            logger.error("Ungültiges Datum. Bitte JJJJ-MM-TT verwenden.")
            return
    if alarm is not None:
        if alarm < 0:
            logger.error("Alarm muss eine positive Zahl sein.")
            return
        ev["alarm"] = alarm
    save_project(data, DB_PATH)
    logger.info("Termin aktualisiert")


def sync_caldav(
    url: str,
    user: str | None = None,
    password: str | None = None,
    group: str = "default",
) -> list[dict[str, str]] | bool:
    """Termine mit CalDAV-Server abgleichen."""
    groups, data = _load_groups()
    if user is None or password is None:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        cal = Calendar.from_ical(resp.text)
        local = groups.get(group, [])
        conflicts: list[dict[str, str]] = []
        for comp in cal.walk("VEVENT"):
            uid = str(comp.get("UID"))
            summary = str(comp.get("SUMMARY"))
            for ev in local:
                if ev.get("uid") == uid and ev.get("title") != summary:
                    conflicts.append(
                        {
                            "uid": uid,
                            "summary": summary,
                            "local": ev["title"],
                            "server": summary,
                        }
                    )
        return conflicts

    events = groups.get(group, [])
    if not events:
        logger.info("Keine Termine zum Synchronisieren in Gruppe '%s'.", group)
        return False
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Kalendertool//DE"]
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    for ev in events:
        date = datetime.fromisoformat(ev["date"]).strftime("%Y%m%d")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{ev['uid']}",
                f"DTSTAMP:{stamp}",
                f"DTSTART;VALUE=DATE:{date}",
                f"SUMMARY:{ev['title']}",
            ]
        )
        if ev.get("alarm") is not None:
            lines.extend(
                [
                    "BEGIN:VALARM",
                    f"TRIGGER:-PT{ev['alarm']}M",
                    "ACTION:DISPLAY",
                    f"DESCRIPTION:{ev['title']}",
                    "END:VALARM",
                ]
            )
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    ical_data = "\n".join(lines)
    for attempt in range(3):
        try:
            resp = requests.put(
                url,
                data=ical_data.encode("utf-8"),
                headers={"Content-Type": "text/calendar"},
                auth=(user, password),
                timeout=10,
            )
            if resp.status_code >= 400:
                raise RuntimeError(f"Serverantwort {resp.status_code}")
            logger.info("CalDAV-Synchronisation erfolgreich")
            return True
        except RequestException as exc:
            wait = 2**attempt
            logger.warning(
                "CalDAV-Synchronisation fehlgeschlagen (%s). Neuer Versuch in %ss",
                exc,
                wait,
            )
            time.sleep(wait)
        except Exception as exc:  # pragma: no cover
            logger.error("CalDAV-Synchronisation fehlgeschlagen: %s", exc)
            return False
    logger.error("CalDAV-Synchronisation abgebrochen nach mehreren Versuchen")
    return False


def main() -> None:
    """Einstiegspunkt für die CLI."""
    setup_logging()
    parser = argparse.ArgumentParser(description="Kalender per Kommandozeile bedienen")
    sub = parser.add_subparsers(dest="cmd")

    add_p = sub.add_parser("add", help="Termin anlegen")
    add_p.add_argument("title")
    add_p.add_argument("date")
    add_p.add_argument("--alarm", type=int)
    add_p.add_argument("--group", default="default")

    export_p = sub.add_parser("export", help="iCal exportieren")
    export_p.add_argument("path")
    export_p.add_argument("--group", default="default")
    export_p.add_argument("--force", action="store_true")

    rem_p = sub.add_parser("remove", help="Termin löschen")
    rem_p.add_argument("index", type=int)

    args = parser.parse_args()
    if args.cmd == "add":
        add_event(args.title, args.date, alarm=args.alarm, group=args.group)
    elif args.cmd == "export":
        export_ical(Path(args.path), group=args.group, force=args.force)
    elif args.cmd == "remove":
        remove_event(args.index)
    else:
        parser.print_help()


__all__ = [
    "add_event",
    "export_ical",
    "_load_groups",
    "sync_caldav",
    "remove_event",
    "edit_event",
    "close",
    "main",
]
