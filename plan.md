# Umsetzungsplan

Dieser Plan wird nach jeder Arbeitsrunde aktualisiert.

## Vorbereitung
- `git pull` (holt aktuelle Dateien aus dem Code-Speicher, "Repository")
- `python3 -m venv venv` (erstellt eine isolierte Arbeitsumgebung, "virtuelle Umgebung")
- `source venv/bin/activate` (aktiviert die virtuelle Umgebung)
- `pip install -r requirements.txt` (installiert notwendige Zusatzprogramme, "Abhängigkeiten")

## Aufgaben
- Fenstergröße flexibel machen
- Keine waagerechten Scrollbalken
- Vier Farb-Themes nach Kontrast-Standards
- Code analysieren und verbessern
- Bedienung nur über Buttons oder Dialoge
- Jede Funktion mit Beschreibung, Tooltip und Hilfe
- Ressourcen schonen
- Standards, Best Practices und Barrierefreiheit
- Portabilität für Linux
- Einheitliche Namen
- Schriftgrößen flexibel
- Klarer Hilfetext
- Vollautomatische Prüfungen und Selbstreparatur
- Autonome Startprüfung

## Nach jedem Schritt
- Tests ausführen: `python -m py_compile videobatch_gui.py videobatch_extra.py videobatch_launcher.py`
- Fortschritt ergänzen: `echo "$(date +%d.%m.%Y) - Fortschritt: <zahl>%" >> fortschritt.txt`
- `todo.txt` und diesen Plan anpassen
- `Entwicklerdoku.md` pflegen: `nano Entwicklerdoku.md` (Textdatei bearbeiten)
- Änderungen sichern: `git add .` und `git commit -m "<nachricht>"`
