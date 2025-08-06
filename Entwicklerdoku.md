# Entwicklerdokumentation

## Architektur
Dieses Tool besteht aus drei Hauptdateien:
- `videobatch_gui.py` (grafische Bedienoberfläche)
- `videobatch_extra.py` (zusätzliche Funktionen)
- `videobatch_launcher.py` (Startprogramm)

## Installation
1. `python3 -m venv venv` (erstellt eine isolierte Arbeitsumgebung, "virtuelle Umgebung")
2. `source venv/bin/activate` (aktiviert die virtuelle Umgebung)
3. `pip install -r requirements.txt` (installiert zusätzliche Programme, "Abhängigkeiten")

## Tests
- `python -m py_compile videobatch_gui.py videobatch_extra.py videobatch_launcher.py` (prüft den Quelltext auf Syntaxfehler)

## Beitrag leisten
- Änderungen mit `git add <datei>` (Datei für Versionsspeicher vormerken) und `git commit -m "Nachricht"` (Änderung speichern) sichern.
- Bei neuen Bedienelementen `setToolTip` (Kurzinfo beim Zeigen) und `setStatusTip` (Hinweis in der Statusleiste) setzen.
