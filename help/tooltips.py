"""Sammlung von Kurzinfos (Tooltips) für Buttons."""

from config.standards import TOOLTIP_DIALOG_SUFFIX

TIP_ADD_IMAGES = "Bilder wählen (PNG, JPG)" + TOOLTIP_DIALOG_SUFFIX
TIP_ADD_AUDIOS = "Audios wählen (MP3, WAV, FLAC)" + TOOLTIP_DIALOG_SUFFIX
TIP_AUTO_PAIR = (
    "Bilder und Audios automatisch zuordnen" " (gleiche Dateinamen werden verbunden)"
)
TIP_START_ENCODE = (
    "Umwandlung starten" " (erstellt Videos und zeigt den Fortschritt in der Liste)"
)
TIP_CLEAR_LIST = (
    "Alle Listen leeren" " (entfernt alle Einträge dauerhaft aus der Tabelle)"
)
TIP_SAVE_PROJECT = (
    "Projekt speichern" " (legt eine SQLite-Datenbank zum späteren Fortsetzen an)"
)
TIP_LOAD_PROJECT = "Projekt laden" " (lädt eine zuvor gespeicherte Datenbankdatei)"
TIP_SHOW_PATH = "Pfad zeigen" " (zeigt den Speicherort der ausgewählten Datei unten an)"
TIP_UNDO = "Letzte Aktion rückgängig" " (stellt gelöschte Zeilen wieder her)"
TIP_STOP = "Vorgang stoppen" " (bricht die aktuelle Umwandlung sofort ab)"
