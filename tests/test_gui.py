import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.append(str(Path(__file__).resolve().parents[1]))

from PySide6 import QtWidgets  # noqa: E402
from videobatch_gui import MainWindow, check_ffmpeg, human_time  # noqa: E402


def test_human_time_gui():
    assert human_time(65) == "01:05"


def test_check_ffmpeg(monkeypatch):
    monkeypatch.setattr("videobatch_gui.which", lambda x: "/usr/bin/" + x)
    assert check_ffmpeg()
    monkeypatch.setattr("videobatch_gui.which", lambda x: None)
    assert not check_ffmpeg()


def test_set_theme(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = MainWindow()
    win._set_theme("Dunkel")
    assert win._theme == "Dunkel"
    assert QtWidgets.QApplication.instance().styleSheet() == win.THEMES["Dunkel"]
    win.close()
