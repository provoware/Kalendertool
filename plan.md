# Umsetzungsplan

Dieser Plan wird nach jeder Arbeitsrunde aktualisiert.

## Vorbereitung
- `git pull` (holt aktuelle Dateien aus dem Code-Speicher, "Repository")
- `python3 -m venv venv` (erstellt eine isolierte Arbeitsumgebung, "virtuelle Umgebung")
- `source venv/bin/activate` (aktiviert die virtuelle Umgebung)
- `pip install -r requirements.txt` (installiert notwendige Zusatzprogramme, "Abhängigkeiten")

## Aufgaben
- Code analysieren und verbessern

## Erledigt
- Fenstergröße flexibel machen
- Vier Farb-Themes nach Kontrast-Standards
- Schriftgrößen flexibel
- Keine waagerechten Scrollbalken
- Bedienung nur über Buttons oder Dialoge (z. B. Button "Pfad zeigen")
- Standards, Best Practices und Barrierefreiheit (Tab-Reihenfolge für Tastenbedienung)
- Klarer Hilfetext
- Vollautomatische Prüfungen
- Selbstreparatur
- Autonome Startprüfung
- Ressourcen schonen
- Portabilität für Linux (Pfadbehandlung mit `pathlib`)
- Eingabefelder und Buttons mit zugänglichen Namen und Hilfetexten
- Fehlerbehandlung erweitert (ffmpeg-Prüfung, automatische Korrektur der Audio-Bitrate)
- Vorschaubilder optional, um Speicher zu sparen
- Notizbereich speichert Aufgaben dauerhaft

- requirements.txt und pyproject.toml angelegt
- Lizenzdatei und README erweitert
- Automatische Tests (GitHub Actions) eingerichtet
- pre-commit mit black und ruff hinzugefügt
- Skript für ausführbares Paket vorbereitet
## Nach jedem Schritt
- Tests ausführen: `python -m py_compile videobatch_gui.py videobatch_extra.py videobatch_launcher.py`
- Fortschritt ergänzen: `echo "$(date +%d.%m.%Y) - Fortschritt: <zahl>%" >> fortschritt.txt`
- `todo.txt` und diesen Plan anpassen
- `Entwicklerdoku.md` pflegen: `nano Entwicklerdoku.md` (Textdatei bearbeiten)
- Änderungen sichern: `git add .` und `git commit -m "<nachricht>"`
