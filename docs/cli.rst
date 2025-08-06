CLI nutzen
==========

Termine lassen sich über die Kommandozeile verwalten:

1. Termin anlegen:

   .. code-block:: bash

      python start_cli.py add "Meeting" 2025-12-24

2. Termine anzeigen:

   .. code-block:: bash

      python start_cli.py list

3. Termine als iCal exportieren:

   .. code-block:: bash

      python start_cli.py export events.ics

Die Datei ``events.ics`` kann in gängige Kalender importiert werden.
