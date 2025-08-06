import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["HOME"] = "/tmp"
sys.path.append(str(Path(__file__).resolve().parents[1]))

from PySide6 import QtGui, QtWidgets  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402
from videobatch_gui import MainWindow, human_time, make_thumb, PairItem  # noqa: E402
from utils import check_ffmpeg  # noqa: E402
from storage import load_project  # noqa: E402
from config.paths import DEFAULT_OUT_DIR, NOTES_FILE  # noqa: E402


def test_human_time_gui():
    assert human_time(65) == "01:05"


def test_check_ffmpeg(monkeypatch):
    monkeypatch.setattr("utils.which", lambda x: "/usr/bin/" + x)
    assert check_ffmpeg()
    monkeypatch.setattr("utils.which", lambda x: None)
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


def test_placeholders_and_defaults(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = MainWindow()
    assert win.out_dir_edit.placeholderText() == f"Standard: {DEFAULT_OUT_DIR}"
    assert win.abitrate_edit.placeholderText() == "z.B. 192k (Kilobit pro Sekunde)"
    win.out_dir_edit.setText("")
    win.abitrate_edit.setText("")
    settings = win._gather_settings()
    assert settings["out_dir"] == str(DEFAULT_OUT_DIR)
    assert settings["abitrate"] == "192k"
    win.close()


def test_input_edge_cases(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = MainWindow()
    validator = win.abitrate_edit.validator()
    state, _, _ = validator.validate("256K", 0)
    assert state == QtGui.QValidator.Acceptable
    state, _, _ = validator.validate("abc", 0)
    assert state == QtGui.QValidator.Invalid
    win.width_spin.setValue(10)
    assert win.width_spin.value() == 16
    win.width_spin.setValue(10000)
    assert win.width_spin.value() == 7680
    win.height_spin.setValue(10)
    assert win.height_spin.value() == 16
    win.height_spin.setValue(10000)
    assert win.height_spin.value() == 4320
    win.close()


def test_abitrate_normalization(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = MainWindow()
    win.abitrate_edit.setText("256")
    assert win._gather_settings()["abitrate"] == "256k"
    win.abitrate_edit.setText("abc")
    assert win._gather_settings()["abitrate"] == "192k"
    win.close()


def test_toggle_thumbnails(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from PIL import Image

    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10), "white").save(img_path)
    win = MainWindow()
    win.show_thumbs.setChecked(False)
    win.model.add_pairs([PairItem(str(img_path))])
    idx = win.model.index(0, 1)
    assert win.model.data(idx, Qt.DecorationRole) is None
    win.show_thumbs.setChecked(True)
    assert isinstance(win.model.data(idx, Qt.DecorationRole), QtGui.QPixmap)
    win.close()


def test_notes_persist(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    notes_file = NOTES_FILE
    if notes_file.exists():
        notes_file.unlink()
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = MainWindow()
    win.notes_edit.setPlainText("Testnotiz")
    win.close()
    assert notes_file.read_text(encoding="utf-8") == "Testnotiz"


def test_project_autosave(tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from PIL import Image

    img_path = tmp_path / "img.png"
    Image.new("RGB", (10, 10), "white").save(img_path)
    win = MainWindow()
    win.model.add_pairs([PairItem(str(img_path))])
    win.close()
    from config.paths import PROJECT_DB

    data = load_project(PROJECT_DB)
    assert data["pairs"][0]["image"].endswith("img.png")


def test_start_encode_requires_ffmpeg(monkeypatch, tmp_path):
    os.environ["XDG_CONFIG_HOME"] = str(tmp_path)
    QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    win = MainWindow()
    win.pairs = [PairItem("a.jpg", "b.mp3")]
    monkeypatch.setattr("videobatch_gui.check_ffmpeg", lambda: False)
    called = {}

    def fake_critical(parent, title, msg):
        called["msg"] = msg

    monkeypatch.setattr(QtWidgets.QMessageBox, "critical", fake_critical)
    win._start_encode()
    assert called["msg"].startswith("FFmpeg")
    win.close()
