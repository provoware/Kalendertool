import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.append(str(Path(__file__).resolve().parents[1]))

from PySide6 import QtWidgets  # noqa: E402
from videobatch_gui import (  # noqa: E402
    MainWindow,
    check_ffmpeg,
    human_time,
    make_thumb,
    PairItem,
)


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


def test_make_thumb_caching(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from PIL import Image

    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10), "white").save(img_path)
    make_thumb.cache_clear()
    make_thumb(str(img_path))
    assert make_thumb.cache_info().hits == 0
    make_thumb(str(img_path))
    assert make_thumb.cache_info().hits == 1


def test_show_selected_path_button(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from PIL import Image

    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10), "white").save(img_path)
    win = MainWindow()
    win.model.add_pairs([PairItem(str(img_path))])
    win.table.selectRow(0)
    win.btn_show_path.click()
    assert win.statusBar().currentMessage() == "img.png"
    win.close()
