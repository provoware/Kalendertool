CLI nutzen
==========

Termine lassen sich über die Kommandozeile verwalten:

#. Termin anlegen:

   .. code-block:: bash

      python start_cli.py add "Meeting" 2025-12-24

#. Termine anzeigen:

   .. code-block:: bash

      python start_cli.py list

#. Termin bearbeiten:

   .. code-block:: bash

      python start_cli.py edit 0 --title "Neuer Titel" --date 2025-12-25 --alarm 60

#. Termine als iCal exportieren:

   .. code-block:: bash

      python start_cli.py export events.ics

   Vorhandene Datei überschreiben:

   .. code-block:: bash

      python start_cli.py export events.ics --force

Die Datei ``events.ics`` kann in gängige Kalender importiert werden.
