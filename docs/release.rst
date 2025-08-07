Release-Prozess
================

1. Versionsnummer anpassen ("Version" = eindeutige Nummer der Softwareausgabe)
   ``sed -i 's/^version = \".*\"/version = \"X.Y.Z\"/' pyproject.toml``
   Ersetzt die alte Versionsnummer.
2. Änderungen eintragen ("CHANGELOG" = Liste der Änderungen)
   Stelle sicher, dass alle Neuerungen im CHANGELOG stehen und füge die Versionsüberschrift ein.
3. Prüfungen ausführen ("Tests" = automatische Überprüfungen)
   ``pre-commit run --all-files``
   ``pytest``
   Formatiert den Code und führt Tests aus.
4. Paket bauen ("Build" = Erstellen einer installierbaren Datei)
   ``python -m build``
   Erstellt das Paket im Ordner ``dist/``.
5. Veröffentlichung markieren ("Tag" = Git-Markierung)
   ``git tag -a vX.Y.Z -m "Version X.Y.Z"``
   ``git push origin vX.Y.Z``
   Kennzeichnet den Release-Stand.
6. Paket hochladen ("Publish" = Bereitstellen für andere Nutzer)
   ``twine upload dist/*``
   Lädt das Paket auf PyPI hoch.
