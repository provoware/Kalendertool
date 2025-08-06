"""Einfache Kalender-CLI mit Speicher in SQLite."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from storage import load_project, save_project, close
from config.paths import PROJECT_DB, ensure_directories

DB_PATH = PROJECT_DB


def _load_events() -> tuple[list[dict[str, str]], dict]:
    """Termine und Rohdaten laden (Datenbankabfrage)."""
    ensure_directories()
    data = load_project(DB_PATH)
    return data.setdefault("events", []), data


def add_event(title: str, date_str: str) -> None:
    """Termin speichern."""
    try:
        date = datetime.fromisoformat(date_str)
    except ValueError:
        print("Ungültiges Datum. Bitte JJJJ-MM-TT verwenden.")
        return
    events, data = _load_events()
    events.append({"title": title, "date": date.isoformat()})
    save_project(data, DB_PATH)
    print(f"Termin '{title}' am {date.date()} gespeichert.")


def list_events() -> None:
    """Alle Termine anzeigen."""
    events, _ = _load_events()
    if not events:
        print("Keine Termine vorhanden.")
        return
    for event in events:
        print(f"{event['date']}: {event['title']}")


def export_ical(file_path: Path) -> None:
    """Termine als iCal-Datei exportieren."""
    events, _ = _load_events()
    if not events:
        print("Keine Termine zum Export vorhanden.")
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
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    try:
        file_path.write_text("\n".join(lines), encoding="utf-8")
    except OSError as exc:
        print(f"Export fehlgeschlagen: {exc}")
        return
    print(f"iCal-Datei unter {file_path} erstellt.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Kalender per Kommandozeile bedienen")
    sub = parser.add_subparsers(dest="cmd")

    add_p = sub.add_parser("add", help="Termin anlegen")
    add_p.add_argument("title", help="Bezeichnung des Termins")
    add_p.add_argument("date", help="Datum im Format JJJJ-MM-TT")

    sub.add_parser("list", help="Termine anzeigen")

    export_p = sub.add_parser("export", help="Termine als iCal exportieren")
    export_p.add_argument("file", help="Zieldatei, z.B. events.ics")

    args = parser.parse_args()
    ensure_directories()
    if args.cmd == "add":
        add_event(args.title, args.date)
    elif args.cmd == "list":
        list_events()
    elif args.cmd == "export":
        export_ical(Path(args.file))
    else:
        parser.print_help()
    close()


if __name__ == "__main__":
    main()
