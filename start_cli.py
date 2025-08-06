"""Einfache Kalender-CLI mit Speicher in SQLite."""

from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import requests
from requests import RequestException

from storage import load_project, save_project, close
from config.paths import PROJECT_DB, ensure_directories
from logging_config import setup_logging

DB_PATH = PROJECT_DB
logger = logging.getLogger(__name__)


def _load_groups() -> tuple[dict[str, list[dict[str, str]]], dict]:
    """Gruppen und Rohdaten laden (Datenbankabfrage)."""
    ensure_directories()
    data = load_project(DB_PATH)
    groups = data.setdefault("groups", {})
    if "events" in data:  # Migration alter Struktur
        groups.setdefault("default", []).extend(data.pop("events"))
    groups.setdefault("default", [])
    return groups, data


def add_event(
    title: str, date_str: str, alarm: int | None = None, group: str = "default"
) -> None:
    """Termin in einer Gruppe speichern."""
    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        logger.error("Ungültiges Datum. Bitte JJJJ-MM-TT verwenden.")
        return
    if alarm is not None and alarm < 0:
        logger.error("Alarm muss eine positive Zahl sein.")
        return
    groups, data = _load_groups()
    entry = {"title": title, "date": date.isoformat()}
    if alarm is not None:
        entry["alarm"] = alarm
    groups.setdefault(group, []).append(entry)
    save_project(data, DB_PATH)
    logger.info(
        "Termin '%s' am %s in Gruppe '%s' gespeichert", title, date.date(), group
    )


def list_events(group: str | None = None) -> None:
    """Alle Termine anzeigen."""
    groups, _ = _load_groups()
    if group:
        events = groups.get(group, [])
        if not events:
            logger.info("Keine Termine in Gruppe '%s'.", group)
            return
        for event in events:
            alarm = (
                f" (Alarm {event['alarm']} min vorher)" if event.get("alarm") else ""
            )
            logger.info("%s: %s%s", event["date"], event["title"], alarm)
        return
    if not any(groups.values()):
        logger.info("Keine Termine vorhanden.")
        return
    for grp, events in groups.items():
        for event in events:
            alarm = (
                f" (Alarm {event['alarm']} min vorher)" if event.get("alarm") else ""
            )
            logger.info("[%s] %s: %s%s", grp, event["date"], event["title"], alarm)


def export_ical(file_path: Path, group: str = "default") -> None:
    """Termine einer Gruppe als iCal-Datei exportieren."""
    groups, _ = _load_groups()
    events = groups.get(group, [])
    if not events:
        logger.info("Keine Termine zum Export in Gruppe '%s'.", group)
        return
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Kalendertool//DE",
    ]
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for ev in events:
        date = datetime.fromisoformat(ev["date"]).strftime("%Y%m%d")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uuid4()}",
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


def sync_caldav(url: str, user: str, password: str, group: str = "default") -> None:
    """Termine einer Gruppe per CalDAV synchronisieren."""
    groups, _ = _load_groups()
    events = groups.get(group, [])
    if not events:
        logger.info("Keine Termine zum Synchronisieren in Gruppe '%s'.", group)
        return
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Kalendertool//DE",
    ]
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for ev in events:
        date = datetime.fromisoformat(ev["date"]).strftime("%Y%m%d")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uuid4()}",
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
            return
        except RequestException as exc:  # pragma: no cover - Netzwerkfehler
            wait = 2**attempt
            logger.warning(
                "CalDAV-Synchronisation fehlgeschlagen (%s). Neuer Versuch in %ss",
                exc,
                wait,
            )
            time.sleep(wait)
        except Exception as exc:  # pragma: no cover - sonstige Fehler
            logger.error("CalDAV-Synchronisation fehlgeschlagen: %s", exc)
            return
    logger.error("CalDAV-Synchronisation abgebrochen nach mehreren Versuchen")


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
    add_p.add_argument(
        "--group",
        default="default",
        help="Name der Gruppe (z.B. familie)",
    )

    list_p = sub.add_parser("list", help="Termine anzeigen")
    list_p.add_argument(
        "--group",
        help="Nur Termine dieser Gruppe anzeigen",
    )

    export_p = sub.add_parser("export", help="Termine als iCal exportieren")
    export_p.add_argument("file", help="Zieldatei, z.B. events.ics")
    export_p.add_argument(
        "--group",
        default="default",
        help="Nur Termine dieser Gruppe exportieren",
    )

    sync_p = sub.add_parser("sync", help="Termine per CalDAV synchronisieren")
    sync_p.add_argument("url", help="CalDAV-URL")
    sync_p.add_argument("user", help="Benutzername")
    sync_p.add_argument("password", help="Passwort")
    sync_p.add_argument(
        "--group",
        default="default",
        help="Nur Termine dieser Gruppe synchronisieren",
    )

    args = parser.parse_args()
    ensure_directories()
    if args.cmd == "add":
        add_event(args.title, args.date, args.alarm, args.group)
    elif args.cmd == "list":
        list_events(args.group)
    elif args.cmd == "export":
        export_ical(Path(args.file), args.group)
    elif args.cmd == "sync":
        sync_caldav(args.url, args.user, args.password, args.group)
    else:
        parser.print_help()
    close()


if __name__ == "__main__":
    main()
