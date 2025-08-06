"""Sphinx-Konfiguration für die Projektdokumentation."""

import sys
from pathlib import Path

project = "Kalendertool"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]
templates_path = ["_templates"]
exclude_patterns = []
html_theme = "alabaster"
