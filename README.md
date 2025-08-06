# Kalendertool

Ein kleines Werkzeug, das Bilder und Tonspuren zu einem Video verbindet.

## Start
- `python3 videobatch_gui.py` (öffnet die grafische Oberfläche)

## Tests
- `python -m py_compile videobatch_gui.py videobatch_extra.py videobatch_launcher.py` (prüft den Quelltext auf Syntaxfehler)
- `pytest -q` (führt automatische Prüfungen aus)

Die Eingabefelder zeigen Beispielwerte (Platzhalter) und nutzen passende
Vorgaben, wenn nichts eingetragen wird. Große Knöpfe haben klare Texte,
lassen sich über die Tastatur erreichen und besitzen kurze Hilfetexte
(Tooltips: kleine Hinweisfenster beim Zeigen).

Vor dem Start wird automatisch geprüft, ob **FFmpeg** (Programm zum Umwandeln
von Medien) vorhanden ist. Bei reinen Zahlen ergänzt das Tool den Buchstaben
"k" (Kilobit), damit die Audio-Bitrate (Tonqualität in Bits pro Sekunde) gültig
ist.

