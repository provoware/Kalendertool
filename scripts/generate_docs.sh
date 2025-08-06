#!/bin/bash
set -e
# API-Dokumentation erzeugen und HTML bauen
sphinx-apidoc -o docs/api api
sphinx-build -b html docs docs/_build
