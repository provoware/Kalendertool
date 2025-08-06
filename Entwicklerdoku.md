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
- `pytest` (führt automatische Tests aus)

## Beitrag leisten
- Änderungen mit `git add <datei>` (Datei für Versionsspeicher vormerken) und `git commit -m "Nachricht"` (Änderung speichern) sichern.
- Bei neuen Bedienelementen `setToolTip` (Kurzinfo beim Zeigen) und `setStatusTip` (Hinweis in der Statusleiste) setzen.
- `setAccessibleName` (Name für Screenreader) verwenden, damit die Oberfläche für alle zugänglich ist.
- Die Oberfläche bietet vier Farb-Themes und anpassbare Schriftgröße; neue Widgets sollen diese Vorgaben übernehmen.
- Tabellen zeigen nur Dateinamen und blenden horizontale Scrollbalken aus; volle Pfade stehen als Tooltip bereit.
- Interaktionen erfolgen über Buttons oder Dialoge, z. B. zeigt der Button "Pfad zeigen" den Speicherort eines Eintrags an.
- Die Tab-Reihenfolge der wichtigsten Elemente wird mit `setTabOrder` (Reihenfolge für Tastatur-Bedienung) festgelegt.
- Der Starter (`videobatch_launcher.py`) prüft beim Start automatisch auf fehlende Pakete oder `ffmpeg` und versucht, alles selbst zu installieren.
- Vorschaubilder werden mit einem Zwischenspeicher (`lru_cache`) nur einmal erzeugt, um Rechenzeit zu sparen.
- Dateipfade werden mit `pathlib.Path` verwaltet, damit das Tool auf verschiedenen Systemen funktioniert.
