# Changelog
Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei festgehalten.
Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.0.0/) und Semantic Versioning.

## [Unreleased]

### Hinzugefügt
- Gruppen-Kalender mit `--group`-Option in der CLI.
- CalDAV-Synchronisation über den Befehl `sync`.
- GUI unterstützt Gruppen-Kalender.
- Dokumentation zu Gruppen-Kalender und CalDAV.
- Löschfunktion in der GUI und Rückmeldung zur Synchronisation.
- Bearbeitungsfunktion für bestehende Termine in CLI und GUI.

### Verbessert
- CalDAV-Synchronisation wiederholt Übertragungen bei Netzwerkfehlern.
- iCal-Export verweigert Überschreiben ohne `--force`.
- GUI füllt Felder bei Auswahl automatisch und meldet Eingabefehler.
- GUI prüft Gruppenfeld und zeigt Hilfetexte (Tooltips) an.

## [0.1.1] - 2025-08-06
### Hinzugefügt
- Zentrales CHANGELOG nach *Keep a Changelog*-Standard.
- Logging-Mechanismus mit zentraler Konfiguration.
- Skripte in `/scripts` verschoben und Dokumentations-Skript ergänzt.
- Sphinx erstellt API-Dokumentation automatisch.
- CI baut nun auch die Dokumentation.
- Markdown-Dateien in `/docs` organisiert.
- Logrotation begrenzt die Logdateigröße.

### Entfernt
- Veraltete Tracking-Dateien `plan.md`, `fortschritt.txt` und `todo.md`.
