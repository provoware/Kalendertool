#!/usr/bin/env bash
set -euo pipefail
pre-commit run --all-files
pytest
rm -rf dist
python3 -m build
python3 -m twine upload "$@" dist/*
