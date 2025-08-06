Konflikt-Dialog
===============

Beim Abgleich mit einem CalDAV-Server können Konflikte entstehen,
wenn ein Termin sowohl lokal als auch auf dem Server geändert wurde.
In diesem Fall zeigt das Programm einen Dialog an.

Der Dialog nutzt ``tkinter.messagebox`` und bietet die Wahl zwischen
der lokalen und der Server-Version. Nach der Entscheidung wird die
Kalenderansicht aktualisiert.

