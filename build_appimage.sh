#!/bin/sh
set -e

# Build a standalone binary via PyInstaller
pyinstaller --noconfirm --onefile videobatch_gui.py

# Prepare AppDir structure
APPDIR=AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp dist/videobatch_gui "$APPDIR/usr/bin/kalendertool"

# Minimal desktop entry
cat <<DESKTOP > "$APPDIR/kalendertool.desktop"
[Desktop Entry]
Type=Application
Name=Kalendertool
Exec=kalendertool
Icon=kalendertool
Categories=Utility;
DESKTOP

# Create AppImage (appimagetool must be installed)
appimagetool "$APPDIR" Kalendertool.AppImage
