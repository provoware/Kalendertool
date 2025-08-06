Gruppen und CalDAV-Synchronisation
=================================

Dieser Abschnitt beschreibt den Ablauf der Kalenderabgleiche.

1. Termine erhalten beim Anlegen eine eindeutige Kennung (UID).
2. Beim Synchronisieren wird der Kalender vom Server abgerufen
   (``requests.get``) und mit ``icalendar`` eingelesen.
3. Ereignisse werden anhand der UID verglichen.
4. Abweichungen mit neuerem Zeitstempel (DTSTAMP) werden als Konflikt
   gemeldet und nicht automatisch überschrieben.
5. Die Funktion liefert eine Konfliktliste zurück, damit der Aufrufer
   entscheiden kann, welche Version behalten wird.

So bleibt der Gruppen-Kalender konsistent, ohne dass Änderungen
verloren gehen.
