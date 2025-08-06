"""Einfache Kalender-CLI mit Speicher in SQLite."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from storage import load_project, save_project, close

DB_PATH = Path("data/project.db")


def _load_events() -> tuple[list[dict[str, str]], dict]:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Kalender per Kommandozeile bedienen")
    sub = parser.add_subparsers(dest="cmd")

    add_p = sub.add_parser("add", help="Termin anlegen")
    add_p.add_argument("title", help="Bezeichnung des Termins")
    add_p.add_argument("date", help="Datum im Format JJJJ-MM-TT")

    sub.add_parser("list", help="Termine anzeigen")

    args = parser.parse_args()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if args.cmd == "add":
        add_event(args.title, args.date)
    elif args.cmd == "list":
        list_events()
    else:
        parser.print_help()
    close()


if __name__ == "__main__":
    main()
