#!/bin/sh
set -e
pre-commit run --all-files
QT_QPA_PLATFORM=offscreen pytest -q
