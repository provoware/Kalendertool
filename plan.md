# Umsetzungsplan

Dieser Plan wird nach jeder Arbeitsrunde aktualisiert.

## Vorbereitung
- `git pull` (holt aktuelle Dateien aus dem Code-Speicher, "Repository")
- `python3 -m venv venv` (erstellt eine isolierte Arbeitsumgebung, "virtuelle Umgebung")
- `source venv/bin/activate` (aktiviert die virtuelle Umgebung)
- `pip install -r requirements.txt` (installiert notwendige Zusatzprogramme, "Abhängigkeiten")

## Aufgaben
- Code analysieren und verbessern
- Bedienung nur über Buttons oder Dialoge
- Ressourcen schonen
- Portabilität für Linux
- Einheitliche Namen
- Vollautomatische Prüfungen und Selbstreparatur
- Autonome Startprüfung

## Erledigt
- Fenstergröße flexibel machen
- Vier Farb-Themes nach Kontrast-Standards
- Schriftgrößen flexibel
- Keine waagerechten Scrollbalken
- Standards, Best Practices und Barrierefreiheit (Tab-Reihenfolge für Tastenbedienung)
- Klarer Hilfetext

## Nach jedem Schritt
- Tests ausführen: `python -m py_compile videobatch_gui.py videobatch_extra.py videobatch_launcher.py`
- Fortschritt ergänzen: `echo "$(date +%d.%m.%Y) - Fortschritt: <zahl>%" >> fortschritt.txt`
- `todo.txt` und diesen Plan anpassen
- `Entwicklerdoku.md` pflegen: `nano Entwicklerdoku.md` (Textdatei bearbeiten)
- Änderungen sichern: `git add .` und `git commit -m "<nachricht>"`
