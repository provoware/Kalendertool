"""Einfache Kalender-CLI mit Speicher in SQLite."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import logging
import requests
from icalendar import Calendar

from storage import load_project, save_project, close
from config.paths import PROJECT_DB, ensure_directories
from logging_config import setup_logging

DB_PATH = PROJECT_DB
logger = logging.getLogger(__name__)


def _load_events() -> tuple[list[dict[str, str]], dict]:
    """Termine und Rohdaten laden (Datenbankabfrage)."""
    ensure_directories()
    data = load_project(DB_PATH)
    return data.setdefault("events", []), data


def add_event(title: str, date_str: str, alarm: int | None = None) -> None:
    """Termin speichern."""
    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        logger.error("Ungültiges Datum. Bitte JJJJ-MM-TT verwenden.")
        return
    if alarm is not None and alarm < 0:
        logger.error("Alarm muss eine positive Zahl sein.")
        return
    events, data = _load_events()
    entry = {
        "uid": str(uuid4()),
        "title": title,
        "date": date.isoformat(),
        "dtstamp": datetime.utcnow().isoformat(),
    }
    if alarm is not None:
        entry["alarm"] = alarm
    events.append(entry)
    save_project(data, DB_PATH)
    logger.info("Termin '%s' am %s gespeichert", title, date.date())


def list_events() -> None:
    """Alle Termine anzeigen."""
    events, _ = _load_events()
    if not events:
        logger.info("Keine Termine vorhanden.")
        return
    for event in events:
        alarm = f" (Alarm {event['alarm']} min vorher)" if event.get("alarm") else ""
        logger.info("%s: %s%s", event["date"], event["title"], alarm)


def export_ical(file_path: Path) -> None:
    """Termine als iCal-Datei exportieren."""
    events, _ = _load_events()
    if not events:
        logger.info("Keine Termine zum Export vorhanden.")
        return
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Kalendertool//DE",
    ]
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
        if ev.get("alarm"):
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
    try:
        file_path.write_text("\n".join(lines), encoding="utf-8")
    except OSError as exc:
        logger.error("Export fehlgeschlagen: %s", exc)
        return
    logger.info("iCal-Datei unter %s erstellt", file_path)


def sync_caldav(url: str) -> list[tuple[dict, dict]]:
    """Kalender vom Server holen und mit lokalen Terminen abgleichen."""
    events, data = _load_events()
    local_by_uid = {ev["uid"]: ev for ev in events}
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Kalender konnte nicht geladen werden: %s", exc)
        return []
    try:
        cal = Calendar.from_ical(resp.text)
    except Exception as exc:  # noqa: BLE001
        logger.error("Kalender konnte nicht gelesen werden: %s", exc)
        return []
    conflicts: list[tuple[dict, dict]] = []
    for comp in cal.walk("VEVENT"):
        uid = str(comp.get("UID"))
        dtstamp = comp.get("DTSTAMP")
        stamp = (
            dtstamp.dt.isoformat()
            if getattr(dtstamp, "dt", None) is not None
            else datetime.utcnow().isoformat()
        )
        remote = {
            "uid": uid,
            "title": str(comp.get("SUMMARY")),
            "date": comp.get("DTSTART").dt.isoformat(),
            "dtstamp": stamp,
        }
        alarm = next((a for a in comp.subcomponents if a.name == "VALARM"), None)
        if alarm is not None:
            trig = alarm.get("TRIGGER")
            if getattr(trig, "dt", None) is not None:
                remote["alarm"] = int(abs(trig.dt.total_seconds()) // 60)
        local = local_by_uid.get(uid)
        if local:
            local_stamp = local.get("dtstamp", "")
            if stamp > local_stamp and (
                local["title"] != remote["title"]
                or local["date"] != remote["date"]
                or local.get("alarm") != remote.get("alarm")
            ):
                conflicts.append((local, remote))
            elif stamp > local_stamp:
                local.update(remote)
        else:
            events.append(remote)
    if conflicts:
        return conflicts
    save_project(data, DB_PATH)
    return []


def main() -> None:
    """Einstiegspunkt für die CLI und Befehlsverarbeitung."""
    setup_logging()
    parser = argparse.ArgumentParser(description="Kalender per Kommandozeile bedienen")
    sub = parser.add_subparsers(dest="cmd")

    add_p = sub.add_parser("add", help="Termin anlegen")
    add_p.add_argument("title", help="Bezeichnung des Termins")
    add_p.add_argument("date", help="Datum im Format JJJJ-MM-TT")
    add_p.add_argument(
        "--alarm",
        type=int,
        help="Erinnerung in Minuten vor dem Termin",
    )

    sub.add_parser("list", help="Termine anzeigen")

    export_p = sub.add_parser("export", help="Termine als iCal exportieren")
    export_p.add_argument("file", help="Zieldatei, z.B. events.ics")

    args = parser.parse_args()
    ensure_directories()
    if args.cmd == "add":
        add_event(args.title, args.date, args.alarm)
    elif args.cmd == "list":
        list_events()
    elif args.cmd == "export":
        export_ical(Path(args.file))
    else:
        parser.print_help()
    close()


if __name__ == "__main__":
    main()
