Gruppen-Kalender und CalDAV
===========================

Mit dem Gruppen-Kalender können mehrere Personen Termine nach Gruppen sortieren.
Die Kommandozeile (CLI) kennt dafür die Option ``--group``.

Beispiel: Termin der Familie anlegen und exportieren::

   python start_cli.py add "Urlaub" 2025-08-01 --group familie
   python start_cli.py export familie.ics --group familie

Existiert ``familie.ics`` bereits, kann sie mit ``--force`` überschrieben werden::

   python start_cli.py export familie.ics --group familie --force

Synchronisation per CalDAV (Kalender-Austauschprotokoll)::

   python start_cli.py sync https://example.com/cal user pass --group familie

Die CalDAV-Synchronisation überträgt die Termine per HTTP ``PUT``.
Fehlermeldungen erscheinen, wenn die Verbindung scheitert. Bei Netzwerkfehlern
versucht die Synchronisation automatisch bis zu drei Mal.

GUI
----

Die grafische Oberfläche (*GUI*) bietet ein Feld für die Gruppe. Das Feld darf
nicht leer bleiben, sonst erscheint eine Fehlermeldung. Beim Überfahren der
Eingabefelder erscheinen kurze Hinweise (Tooltips: kleine Hilfefenster). Über die
Buttons können Termine gespeichert, bearbeitet, gelöscht oder per CalDAV
Synchronisation übertragen werden. Nach dem Speichern, Ändern oder Löschen
erscheint eine Bestätigung; bei Fehlern zeigt die GUI eine entsprechende
Meldung. Nach einer Synchronisation erscheint eine Meldung mit Erfolg oder
Fehlschlag.
Die grafische Oberfläche (*GUI*) bietet ein Feld für die Gruppe. Über die
Buttons können Termine gespeichert oder per CalDAV synchronisiert werden.
