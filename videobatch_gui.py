# =========================================
# QUICKSTART
# Direktstart (wenn alles installiert):  python3 videobatch_gui.py
# Empfohlen (Auto-Setup):                python3 videobatch_launcher.py
# Edit mit micro:                        micro videobatch_gui.py
# =========================================

from __future__ import annotations
import json
import logging
import re
import shutil
import subprocess
import sys
from datetime import datetime
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils import build_out_name, human_time

from api import build_ffmpeg_cmd, run_ffmpeg

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QHeaderView

from config.paths import LOG_FILE, NOTES_FILE
from help.tooltips import (
    TIP_ADD_IMAGES,
    TIP_ADD_AUDIOS,
    TIP_AUTO_PAIR,
    TIP_START_ENCODE,
)

# ---------- Logging & Persistenz ----------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("VideoBatchTool")


# ---------- Helpers ----------
def which(p: str):
    return shutil.which(p)


def check_ffmpeg():
    return which("ffmpeg") and which("ffprobe")


def probe_duration(path: str) -> float:
    try:
        import ffmpeg

        pr = ffmpeg.probe(path)
        fmt = pr.get("format", {})
        if "duration" in fmt:
            return float(fmt["duration"])
        for st in pr.get("streams", []):
            if st.get("codec_type") == "audio":
                return float(st.get("duration", 0) or 0)
    except Exception as e:
        logger.debug("Dauer konnte nicht ermittelt werden: %s", e)
    return 0.0


def get_used_dir() -> Path:
    return Path.home() / "benutzte_dateien"


def default_output_dir() -> Path:
    return Path.home() / "Videos" / "VideoBatchTool_Out"


def normalize_bitrate(text: str) -> str:
    """Ensure audio bitrate has a unit and fallback to default."""
    text = text.strip().lower()
    if not text:
        return "192k"
    m = re.fullmatch(r"(\d+)([km]?)", text)
    if not m:
        return "192k"
    value, unit = m.groups()
    if not unit:
        unit = "k"
    return f"{value}{unit}"


def safe_move(src: Path, dst_dir: Path, copy_only: bool = False) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    tgt = dst_dir / src.name
    if tgt.exists():
        stem, suf = src.stem, src.suffix
        tgt = dst_dir / f"{stem}_{datetime.now().strftime('%Y%m%d-%H%M%S')}{suf}"
    try:
        if copy_only:
            shutil.copy2(src, tgt)
        else:
            shutil.move(src, tgt)
    except Exception as e:
        logger.debug("Verschieben fehlgeschlagen (%s), Kopie wird erstellt", e)
        shutil.copy2(src, tgt)
        if not copy_only:
            try:
                src.unlink()
            except Exception as del_err:
                logger.debug("Quelle konnte nicht gelöscht werden: %s", del_err)
    return tgt


@lru_cache(maxsize=128)
def make_thumb(path: str, size: Tuple[int, int] = (160, 90)) -> QtGui.QPixmap:
    try:
        from PIL import Image

        with Image.open(path) as img:
            img.thumbnail(size)
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            data = img.tobytes("raw", "RGBA")
        qimg = QtGui.QImage(
            data, img.size[0], img.size[1], QtGui.QImage.Format_RGBA8888
        )
        return QtGui.QPixmap.fromImage(qimg)
    except Exception as e:
        logger.debug("Thumbnail-Erstellung fehlgeschlagen: %s", e)
        pix = QtGui.QPixmap(size[0], size[1])
        pix.fill(Qt.gray)
        return pix


# ---------- Datenmodell ----------
COLUMNS = ["#", "Thumb", "Bild", "Audio", "Dauer", "Ausgabe", "Fortschritt", "Status"]


@dataclass
class PairItem:
    image_path: str
    audio_path: Optional[str] = None
    duration: float = 0.0
    output: str = ""
    status: str = "WARTET"
    progress: float = 0.0
    thumb: Optional[QtGui.QPixmap] = field(default=None, repr=False)
    valid: bool = True
    validation_msg: str = ""

    def update_duration(self):
        if self.audio_path:
            self.duration = probe_duration(self.audio_path)

    def load_thumb(self):
        if self.thumb is None and self.image_path:
            self.thumb = make_thumb(self.image_path)

    def validate(self):
        if not self.image_path or not self.audio_path:
            self.valid = False
            self.validation_msg = "Bild oder Audio fehlt"
            return
        ip, ap = Path(self.image_path), Path(self.audio_path)
        if not ip.exists():
            self.valid = False
            self.validation_msg = f"Bild fehlt: {ip}"
            return
        if not ap.exists():
            self.valid = False
            self.validation_msg = f"Audio fehlt: {ap}"
            return
        if ip.suffix.lower() not in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
            self.valid = False
            self.validation_msg = "Ungültiges Bildformat"
            return
        if ap.suffix.lower() not in (".mp3", ".wav", ".flac", ".m4a", ".aac"):
            self.valid = False
            self.validation_msg = "Ungültiges Audioformat"
            return
        self.valid = True
        self.validation_msg = ""


class PairTableModel(QAbstractTableModel):
    def __init__(self, pairs: List[PairItem], show_thumbs: bool = True):
        super().__init__()
        self.pairs = pairs
        self.show_thumbs = show_thumbs

    def rowCount(self, parent=QModelIndex()):
        return len(self.pairs)

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def headerData(self, s, o, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        return COLUMNS[s] if o == Qt.Horizontal else str(s + 1)

    def data(self, idx, role=Qt.DisplayRole):
        if not idx.isValid():
            return None
        item = self.pairs[idx.row()]
        col = idx.column()
        if role == Qt.DisplayRole:
            if col == 0:
                return str(idx.row() + 1)
            if col == 2:
                return Path(item.image_path).name
            if col == 3:
                return Path(item.audio_path).name if item.audio_path else "—"
            if col == 4:
                return human_time(item.duration) if item.duration else "?"
            if col == 5:
                return Path(item.output).name if item.output else "—"
            if col == 6:
                return f"{int(item.progress)}%"
            if col == 7:
                return item.status
        if role == Qt.DecorationRole and col == 1 and self.show_thumbs:
            item.load_thumb()
            return item.thumb
        if role == Qt.ToolTipRole:
            if col in (2, 3, 5):
                return {
                    2: item.image_path,
                    3: item.audio_path or "",
                    5: item.output or "",
                }[col]
            if not item.valid:
                return item.validation_msg
        if role == Qt.ForegroundRole and not item.valid:
            return QtGui.QBrush(Qt.red)
        return None

    def flags(self, idx):
        if not idx.isValid():
            return Qt.NoItemFlags
        f = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if idx.column() in (2, 3, 5):
            f |= Qt.ItemIsEditable
        return f

    def setData(self, idx, value, role=Qt.EditRole):
        if role != Qt.EditRole or not idx.isValid():
            return False
        item = self.pairs[idx.row()]
        col = idx.column()
        if col == 2:
            item.image_path = value
            item.thumb = None
        elif col == 3:
            item.audio_path = value
            item.update_duration()
        elif col == 5:
            item.output = value
        else:
            return False
        item.validate()
        self.dataChanged.emit(idx, idx)
        return True

    def add_pairs(self, new_pairs: List[PairItem]):
        self.beginInsertRows(
            QModelIndex(), len(self.pairs), len(self.pairs) + len(new_pairs) - 1
        )
        self.pairs.extend(new_pairs)
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self.pairs.clear()
        self.endResetModel()


# ---------- Worker ----------
class EncodeWorker(QtCore.QObject):
    row_progress = Signal(int, float)
    overall_progress = Signal(float)
    row_error = Signal(int, str)
    log = Signal(str)
    finished = Signal()

    def __init__(
        self, pairs: List[PairItem], settings: Dict[str, Any], copy_only: bool
    ):
        super().__init__()
        self.pairs = pairs
        self.settings = settings
        self.copy_only = copy_only
        self._stop = False
        self._proc: Optional[subprocess.Popen] = None

    def stop(self):
        self._stop = True
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.kill()
            except Exception as exc:
                self.log.emit(f"Prozess konnte nicht beendet werden: {exc}")

    def run(self):
        total = len(self.pairs)
        for i, item in enumerate(self.pairs):
            if self._stop:
                self.log.emit("Abbruch durch Benutzer.")
                break
            item.validate()
            if not item.valid:
                item.status = "FEHLER"
                self.row_error.emit(i, item.validation_msg)
                continue
            try:
                item.status = "ENCODIERE"
                item.progress = 0.0
                self.row_progress.emit(i, 0.0)
                out_dir = Path(self.settings["out_dir"]).resolve()
                out_dir.mkdir(parents=True, exist_ok=True)
                item.output = build_out_name(item.audio_path, out_dir)
                w, h = self.settings["width"], self.settings["height"]
                crf = self.settings["crf"]
                preset = self.settings["preset"]
                ab = self.settings["abitrate"]
                duration = item.duration or 1
                cmd = build_ffmpeg_cmd(
                    item.image_path,
                    item.audio_path,
                    item.output,
                    w,
                    h,
                    ab,
                    crf,
                    preset,
                )
                self._proc = run_ffmpeg(cmd)
                for line in self._proc.stderr:
                    if self._stop:
                        self._proc.kill()
                        break
                    if "time=" in line:
                        try:
                            t = line.split("time=")[1].split(" ")[0]
                            h_, m_, s_ = t.split(":")
                            elapsed = float(h_) * 3600 + float(m_) * 60 + float(s_)
                            perc = min(100.0, elapsed / duration * 100.0)
                            item.progress = perc
                            self.row_progress.emit(i, perc)
                        except Exception as e:
                            self.log.emit(f"Fortschritt nicht lesbar: {e}")
                self._proc.wait()
                rc = self._proc.returncode
                self._proc = None
                if rc != 0:
                    item.status = "FEHLER"
                    self.row_error.emit(i, "FFmpeg-Fehler")
                else:
                    item.status = "FERTIG"
                    item.progress = 100.0
                    self.row_progress.emit(i, 100.0)
                    self.log.emit(f"Fertig: {item.output}")
            except Exception as e:
                item.status = "FEHLER"
                self.row_error.emit(i, str(e))
            done = sum(1 for p in self.pairs if p.status == "FERTIG")
            self.overall_progress.emit(done / max(1, total) * 100.0)
        if all(p.status == "FERTIG" for p in self.pairs):
            try:
                dst = get_used_dir()
                moved = 0
                for p in self.pairs:
                    for f in (p.image_path, p.audio_path):
                        if f and Path(f).exists():
                            safe_move(Path(f), dst, copy_only=self.copy_only)
                            moved += 1
                self.log.emit(
                    f"{moved} Dateien nach {dst} {'kopiert' if self.copy_only else 'verschoben'}."
                )
            except Exception as e:
                self.log.emit(f"Archivierung fehlgeschlagen: {e}")
        self.finished.emit()


# ---------- UI Widgets ----------
class DropListWidget(QtWidgets.QListWidget):
    files_dropped = Signal(list)

    def __init__(self, title: str, patterns: Tuple[str, ...]):
        super().__init__()
        self.patterns = patterns
        self.setAcceptDrops(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setToolTip(title)
        self.setStatusTip(title)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, e):
        files = [u.toLocalFile() for u in e.mimeData().urls()]
        acc = [f for f in files if f.lower().endswith(self.patterns)]
        if acc:
            self.add_files(acc)
            self.files_dropped.emit(acc)
        e.acceptProposedAction()

    def add_files(self, files: List[str]):
        for f in files:
            it = QtWidgets.QListWidgetItem(Path(f).name)
            it.setData(Qt.UserRole, f)
            self.addItem(it)

    def selected_paths(self) -> List[str]:
        return [i.data(Qt.UserRole) for i in self.selectedItems()]


class HelpPane(QtWidgets.QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setOpenExternalLinks(True)
        self.setHtml(self._html())

    def _html(self) -> str:
        return (
            "<h2>Bedienhilfe</h2>"
            "<ol><li>Bilder und Audios hinzufügen oder ziehen</li>"
            "<li>Auto-Paaren klicken oder Paare selbst wählen</li>"
            "<li>Einstellungen prüfen</li>"
            "<li>START drücken</li></ol>"
            "<ul><li>Dateiname: Audioname plus Zeit</li>"
            "<li>Doppelklick auf eine Zeile ändert Pfade</li>"
            "<li>Kurzhilfe zeigt ganze Pfade</li>"
            "<li>Nach Erfolg werden Dateien archiviert</li></ul>"
        )


class InfoDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.total_label = QtWidgets.QLabel("0")
        self.done_label = QtWidgets.QLabel("0")
        self.err_label = QtWidgets.QLabel("0")
        self.ffmpeg_lbl = QtWidgets.QLabel("ffmpeg: ?")
        self.env_lbl = QtWidgets.QLabel("Env: OK")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximumWidth(240)
        self.mini_log = QtWidgets.QPlainTextEdit()
        self.mini_log.setReadOnly(True)
        self.mini_log.setMaximumBlockCount(300)
        self.mini_log.setFixedHeight(90)
        row = QtWidgets.QHBoxLayout()
        for w in (
            QtWidgets.QLabel("Gesamt:"),
            self.total_label,
            QtWidgets.QLabel("Fertig:"),
            self.done_label,
            QtWidgets.QLabel("Fehler:"),
            self.err_label,
            QtWidgets.QLabel("Progress:"),
            self.progress,
            self.ffmpeg_lbl,
            self.env_lbl,
        ):
            row.addWidget(w)
        row.addStretch(1)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addLayout(row)
        lay.addWidget(self.mini_log)

    def set_counts(self, t, d, e):
        self.total_label.setText(str(t))
        self.done_label.setText(str(d))
        self.err_label.setText(str(e))

    def set_progress(self, v):
        self.progress.setValue(v)

    def set_env(self, ff_ok, imp_ok=True):
        self.ffmpeg_lbl.setText(f"ffmpeg: {'OK' if ff_ok else 'FEHLT'}")
        self.env_lbl.setText(f"Env: {'OK' if imp_ok else 'FEHLT'}")

    def log(self, msg):
        self.mini_log.appendPlainText(msg)


# ---------- MainWindow ----------
class MainWindow(QtWidgets.QMainWindow):
    FONT_STEP = 1
    THEMES = {
        "Hell": "",
        "Dunkel": (
            "QWidget { background:#2b2b2b; color:#f0f0f0; }"
            "QPushButton { background:#3c3c3c; color:#f0f0f0; }"
        ),
        "Blau": (
            "QWidget { background:#e6f0ff; }" "QPushButton { background:#cfe2ff; }"
        ),
        "Kontrast": (
            "QWidget { background:#000000; color:#ffffff; }"
            "QPushButton { background:#000000; color:#ffffff; border:1px solid #ffffff; }"
        ),
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoBatchTool 4.1 – Bild + Audio → MP4")
        screen = QtGui.QGuiApplication.primaryScreen()
        available = screen.availableGeometry()
        width = int(available.width() * 0.8)
        height = int(available.height() * 0.8)
        self.resize(width, height)
        self.setMinimumSize(min(800, width), min(600, height))

        self.settings = QtCore.QSettings("Provoware", "VideoBatchTool")
        self._font_size = self.settings.value("ui/font_size", 11, int)
        self._theme = self.settings.value("ui/theme", "Hell", str)
        show_thumbs = self.settings.value("ui/show_thumbs", True, bool)

        sys.excepthook = self._global_exception

        self.pairs: List[PairItem] = []
        self.model = PairTableModel(self.pairs, show_thumbs)

        self.dashboard = InfoDashboard()
        self.dashboard.set_env(check_ffmpeg(), True)

        self.image_list = DropListWidget(
            "Bilder", (".jpg", ".jpeg", ".png", ".bmp", ".webp")
        )
        self.audio_list = DropListWidget(
            "Audios", (".mp3", ".wav", ".flac", ".m4a", ".aac")
        )
        self.image_list.files_dropped.connect(self._on_images_added)
        self.audio_list.files_dropped.connect(self._on_audios_added)

        pool_tabs = QtWidgets.QTabWidget()
        pool_tabs.addTab(self.image_list, "Bilder")
        pool_tabs.addTab(self.audio_list, "Audios")

        self.table = QtWidgets.QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        for col in (2, 3, 5):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

        self.help_pane = HelpPane()

        # Einstellungen
        self.out_dir_edit = QtWidgets.QLineEdit(
            self.settings.value("encode/out_dir", "", str)
        )
        self.out_dir_edit.setPlaceholderText(f"Standard: {default_output_dir()}")
        self.out_dir_edit.setAccessibleName("Ausgabeordner")
        self.crf_spin = QtWidgets.QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(self.settings.value("encode/crf", 23, int))
        self.crf_spin.setAccessibleName("Qualität")
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.addItems(
            [
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ]
        )
        self.preset_combo.setCurrentText(
            self.settings.value("encode/preset", "ultrafast", str)
        )
        self.preset_combo.setAccessibleName("Geschwindigkeit")
        self.width_spin = QtWidgets.QSpinBox()
        self.width_spin.setRange(16, 7680)
        self.width_spin.setValue(self.settings.value("encode/width", 1920, int))
        self.width_spin.setSuffix(" px")
        self.width_spin.setAccessibleName("Breite")
        self.height_spin = QtWidgets.QSpinBox()
        self.height_spin.setRange(16, 4320)
        self.height_spin.setValue(self.settings.value("encode/height", 1080, int))
        self.height_spin.setSuffix(" px")
        self.height_spin.setAccessibleName("Höhe")
        self.abitrate_edit = QtWidgets.QLineEdit(
            self.settings.value("encode/abitrate", "", str)
        )
        self.abitrate_edit.setPlaceholderText("z.B. 192k (Kilobit pro Sekunde)")
        self.abitrate_edit.setValidator(
            QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"\d+[kKmM]?"))
        )
        self.abitrate_edit.setAccessibleName("Audio-Bitrate")
        self.show_thumbs = QtWidgets.QCheckBox("Vorschau-Bilder anzeigen")
        self.show_thumbs.setToolTip(
            "Zeigt kleine Vorschaubilder, spart Speicher wenn ausgeschaltet"
        )
        self.show_thumbs.setAccessibleName("Vorschau-Bilder anzeigen")
        self.show_thumbs.setChecked(self.model.show_thumbs)
        self.show_thumbs.toggled.connect(self._on_toggle_thumbs)
        self.clear_after = QtWidgets.QCheckBox("Nach Fertigstellung Listen leeren")
        self.clear_after.setChecked(self.settings.value("ui/clear_after", False, bool))

        form = QtWidgets.QFormLayout()
        self._add_form(
            form,
            "Ausgabeordner",
            self.out_dir_edit,
            "Ordner für fertige MP4-Dateien",
        )
        self._add_form(
            form,
            "Qualität",
            self.crf_spin,
            "0 = beste, 23 = normal",
        )
        self._add_form(
            form,
            "Geschwindigkeit",
            self.preset_combo,
            "schneller = größere Datei",
        )
        self._add_form(
            form,
            "Breite",
            self.width_spin,
            "Breite des Videos in Pixel",
        )
        self._add_form(
            form,
            "Höhe",
            self.height_spin,
            "Höhe des Videos in Pixel",
        )
        self._add_form(
            form,
            "Audio-Qualität",
            self.abitrate_edit,
            "z. B. 192k",
        )
        form.addRow("", self.show_thumbs)
        form.addRow("", self.clear_after)

        self.settings_widget = QtWidgets.QWidget()
        self.settings_widget.setLayout(form)

        left_split = QtWidgets.QSplitter(Qt.Vertical)
        left_split.addWidget(pool_tabs)
        left_split.addWidget(self.settings_widget)
        right_split = QtWidgets.QSplitter(Qt.Vertical)
        right_split.addWidget(self.table)
        right_split.addWidget(self.help_pane)
        grid_split = QtWidgets.QSplitter(Qt.Horizontal)
        grid_split.addWidget(left_split)
        grid_split.addWidget(right_split)

        self.progress_total = QtWidgets.QProgressBar()
        self.progress_total.setFormat("%p% gesamt")
        self.log_edit = QtWidgets.QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumBlockCount(5000)
        self.notes_edit = QtWidgets.QPlainTextEdit()
        self.notes_edit.setPlaceholderText("Notizen (werden gespeichert)")
        self.notes_edit.setAccessibleName("Notizfeld")
        self.notes_edit.setToolTip(
            "Eigene Aufgaben oder Hinweise; wird automatisch gespeichert"
        )
        self.notes_edit.setFixedHeight(80)
        try:
            self.notes_edit.setPlainText(NOTES_FILE.read_text(encoding="utf-8"))
        except FileNotFoundError:
            NOTES_FILE.touch()

        log_box = QtWidgets.QWidget()
        bl = QtWidgets.QVBoxLayout(log_box)
        bl.addWidget(self.progress_total)
        bl.addWidget(self.log_edit)
        bl.addWidget(self.notes_edit)

        outer_split = QtWidgets.QSplitter(Qt.Vertical)
        outer_split.addWidget(grid_split)
        outer_split.addWidget(log_box)
        outer_split.setStretchFactor(0, 4)
        outer_split.setStretchFactor(1, 1)

        # Buttons
        self.btn_add_images = QtWidgets.QPushButton("Bilder wählen")
        self.btn_add_images.setToolTip(TIP_ADD_IMAGES)
        self.btn_add_images.setStatusTip(
            "Öffnet einen Dialog zum Auswählen von Bilddateien, z.\u202fB. Urlaub.jpg"
        )

        self.btn_add_audios = QtWidgets.QPushButton("Audios wählen")
        self.btn_add_audios.setToolTip(TIP_ADD_AUDIOS)
        self.btn_add_audios.setStatusTip(
            "Öffnet einen Dialog zum Auswählen von Audiodateien, z.\u202fB. Musik.mp3"
        )

        self.btn_auto_pair = QtWidgets.QPushButton("Auto-Paaren")
        self.btn_auto_pair.setToolTip(
            "Bilder und Audios automatisch verbinden (paart Dateien mit gleichem Namen)"
        )
        self.btn_auto_pair.setToolTip(TIP_AUTO_PAIR)
        self.btn_auto_pair.setStatusTip(
            "Verknüpft die Dateien paarweise ohne manuelle Auswahl"
        )

        self.btn_clear = QtWidgets.QPushButton("Alles löschen")
        self.btn_clear.setToolTip("Alle Listen leeren")
        self.btn_clear.setStatusTip(
            "Entfernt alle geladenen Bilder und Audios aus den Listen"
        )

        self.btn_undo = QtWidgets.QPushButton("Rückgängig")
        self.btn_undo.setToolTip("Letzte Aktion rückgängig machen")
        self.btn_undo.setStatusTip(
            "Stellt den Zustand vor der letzten Änderung wieder her"
        )
        self.btn_undo.setAccessibleName("Rückgängig")

        self.btn_save = QtWidgets.QPushButton("Projekt speichern")
        self.btn_save.setToolTip(
            "Projekt als Datei speichern (JSON-Datei, um später weiterzuarbeiten)"
        )
        self.btn_save.setStatusTip(
            "Speichert aktuelle Paare in einer Datei, z.\u202fB. projekt.json"
        )

        self.btn_load = QtWidgets.QPushButton("Projekt laden")
        self.btn_load.setToolTip("Gespeichertes Projekt öffnen")
        self.btn_load.setStatusTip(
            "Lädt eine Projektdatei und stellt alle Paare wieder her"
        )

        self.btn_show_path = QtWidgets.QPushButton("Pfad zeigen")
        self.btn_show_path.setToolTip("Pfad der Auswahl anzeigen")
        self.btn_show_path.setStatusTip(
            "Zeigt den Speicherort der gewählten Datei unten an"
        )
        self.btn_show_path.clicked.connect(self._show_selected_path)

        self.btn_encode = QtWidgets.QPushButton("Start")
        self.btn_encode.setToolTip(TIP_START_ENCODE)
        self.btn_encode.setStatusTip("Beginnt mit der Erstellung der MP4-Dateien")
        self.btn_encode.setAccessibleName("Start")

        self.btn_stop = QtWidgets.QPushButton("Stopp")
        self.btn_stop.setToolTip("Vorgang stoppen")
        self.btn_stop.setStatusTip("Bricht die laufende Umwandlung ab")
        self.btn_stop.setAccessibleName("Stopp")
        self.btn_stop.setEnabled(False)

        self.btn_encode.setStyleSheet(
            "font-size:16pt;font-weight:bold;background:#005BBB;color:white;padding:6px 14px;"
        )

        top_buttons = QtWidgets.QHBoxLayout()
        for b in (
            self.btn_add_images,
            self.btn_add_audios,
            self.btn_auto_pair,
            self.btn_clear,
            self.btn_undo,
            self.btn_save,
            self.btn_load,
            self.btn_show_path,
            self.btn_encode,
            self.btn_stop,
        ):
            top_buttons.addWidget(b)
        top_buttons.addStretch(1)

        central_layout = QtWidgets.QVBoxLayout()
        central_layout.addWidget(self.dashboard)
        central_layout.addLayout(top_buttons)
        central_layout.addWidget(outer_split)
        central = QtWidgets.QWidget()
        central.setLayout(central_layout)
        self.setCentralWidget(central)

        self.count_label = QtWidgets.QLabel("0 Bilder | 0 Audios | 0 Paare")
        self.statusBar().addPermanentWidget(self.count_label)

        self.copy_only = False
        self._build_menus()
        self._set_theme(self._theme)

        self._history: List[List[PairItem]] = []
        self.thread: Optional[QtCore.QThread] = None
        self.worker: Optional[EncodeWorker] = None

        # Signals
        self.btn_add_images.clicked.connect(self._pick_images)
        self.btn_add_audios.clicked.connect(self._pick_audios)
        self.btn_auto_pair.clicked.connect(self._auto_pair)
        self.btn_clear.clicked.connect(self._clear_all)
        self.btn_undo.clicked.connect(self._undo_last)
        self.btn_save.clicked.connect(self._save_project)
        self.btn_load.clicked.connect(self._load_project)
        self.btn_encode.clicked.connect(self._start_encode)
        self.btn_stop.clicked.connect(self._stop_encode)
        self.table.doubleClicked.connect(self._show_statusbar_path)

        self._set_tab_order()
        self._apply_font()
        self.restoreGeometry(self.settings.value("ui/geometry", b"", bytes))
        self.restoreState(self.settings.value("ui/window_state", b"", bytes))

    # ----- UI helpers -----
    def _build_menus(self):
        menubar = self.menuBar()

        m_datei = menubar.addMenu("Datei")
        act_quit = QAction("Beenden", self)
        act_quit.triggered.connect(self.close)
        m_datei.addAction(act_quit)

        m_ansicht = menubar.addMenu("Ansicht")
        act_font_plus = QAction("Schrift +", self)
        act_font_plus.triggered.connect(lambda: self._change_font(1))
        act_font_minus = QAction("Schrift -", self)
        act_font_minus.triggered.connect(lambda: self._change_font(-1))
        act_font_reset = QAction("Schrift Reset", self)
        act_font_reset.triggered.connect(lambda: self._set_font(11))
        m_ansicht.addActions([act_font_plus, act_font_minus, act_font_reset])

        theme_menu = m_ansicht.addMenu("Theme")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        for name in self.THEMES:
            act = QAction(name, self, checkable=True)
            act.setChecked(name == self._theme)
            act.triggered.connect(
                lambda checked, n=name: self._set_theme(n) if checked else None
            )
            theme_group.addAction(act)
            theme_menu.addAction(act)

        m_option = menubar.addMenu("Optionen")
        self.act_copy_only = QAction(
            "Dateien nur kopieren (nicht verschieben)",
            self,
            checkable=True,
            checked=self.copy_only,
        )
        self.act_copy_only.triggered.connect(self._toggle_copy_mode)
        m_option.addAction(self.act_copy_only)

        m_hilfe = menubar.addMenu("Hilfe")
        act_log = QAction("Logdatei öffnen", self)
        act_log.triggered.connect(
            lambda: QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(str(LOG_FILE))
            )
        )
        m_hilfe.addAction(act_log)

    def _set_tab_order(self):
        """Reihenfolge der Tastatur-Navigation festlegen (Barrierefreiheit)."""
        widgets = [
            self.btn_add_images,
            self.btn_add_audios,
            self.btn_auto_pair,
            self.btn_clear,
            self.btn_undo,
            self.btn_save,
            self.btn_load,
            self.btn_encode,
            self.btn_stop,
            self.table,
        ]
        for a, b in zip(widgets, widgets[1:]):
            self.setTabOrder(a, b)

    def _change_font(self, delta: int):
        self._set_font(self._font_size + delta)

    def _set_font(self, size: int):
        size = max(8, min(32, size))
        self._font_size = size
        self._apply_font()
        self.settings.setValue("ui/font_size", size)

    def _apply_font(self):
        f = QtGui.QFont("DejaVu Sans", self._font_size)
        self.setFont(f)

    def _set_theme(self, name: str):
        QtWidgets.QApplication.instance().setStyleSheet(self.THEMES.get(name, ""))
        self.settings.setValue("ui/theme", name)
        self._theme = name

    def _add_form(
        self,
        layout: QtWidgets.QFormLayout,
        label: str,
        widget: QtWidgets.QWidget,
        help_text: str,
    ):
        widget.setToolTip(help_text)
        widget.setStatusTip(help_text)
        hint = QtWidgets.QLabel(f"<small>{help_text}</small>")
        hint.setWordWrap(True)
        box = QtWidgets.QVBoxLayout()
        box.addWidget(widget)
        box.addWidget(hint)
        wrap = QtWidgets.QWidget()
        wrap.setLayout(box)
        layout.addRow(label, wrap)

    def _log(self, msg: str):
        self.log_edit.appendPlainText(msg)
        self.dashboard.log(msg)
        logger.info(msg)

    def _push_history(self):
        snap = []
        for p in self.pairs:
            q = PairItem(p.image_path, p.audio_path)
            q.duration = p.duration
            q.output = p.output
            q.status = p.status
            q.progress = p.progress
            q.valid = p.valid
            q.validation_msg = p.validation_msg
            snap.append(q)
        self._history.append(snap)
        if len(self._history) > 30:
            self._history.pop(0)

    def _update_counts(self):
        img_count = self.image_list.count()
        aud_count = self.audio_list.count()
        pair_count = sum(1 for p in self.pairs if p.image_path and p.audio_path)
        err_count = sum(1 for p in self.pairs if p.status == "FEHLER")
        fin_count = sum(1 for p in self.pairs if p.status == "FERTIG")
        self.count_label.setText(
            f"{img_count} Bilder | {aud_count} Audios | {pair_count} Paare"
        )
        self.dashboard.set_counts(pair_count, fin_count, err_count)
        running = self.thread is not None and self.thread.isRunning()
        self.btn_encode.setEnabled(pair_count > 0 and not running)

    def _on_toggle_thumbs(self, checked: bool):
        self.model.show_thumbs = checked
        if not checked:
            for p in self.pairs:
                p.thumb = None
        self.table.viewport().update()

    # ----- file actions -----
    def _pick_images(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Bilder wählen",
            str(Path.cwd()),
            "Bilder (*.jpg *.jpeg *.png *.bmp *.webp)",
        )
        if files:
            self._on_images_added(files)

    def _pick_audios(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Audios wählen",
            str(Path.cwd()),
            "Audio (*.mp3 *.wav *.flac *.m4a *.aac)",
        )
        if files:
            self._on_audios_added(files)

    def _on_images_added(self, files: List[str]):
        self._push_history()
        for f in files:
            self.image_list.add_files([f])
            self.model.add_pairs([PairItem(f)])
        self._update_counts()
        self._resize_columns()

    def _on_audios_added(self, files: List[str]):
        self._push_history()
        for f in files:
            self.audio_list.add_files([f])
        it = iter(files)
        for p in self.pairs:
            if p.audio_path is None:
                try:
                    p.audio_path = next(it)
                    p.update_duration()
                    p.validate()
                except StopIteration:
                    break
        self.model.layoutChanged.emit()
        self._update_counts()
        self._resize_columns()

    def _auto_pair(self):
        self._push_history()
        imgs = [
            self.image_list.item(i).data(Qt.UserRole)
            for i in range(self.image_list.count())
        ]
        auds = [
            self.audio_list.item(i).data(Qt.UserRole)
            for i in range(self.audio_list.count())
        ]
        imgs.sort()
        auds.sort()
        self.model.clear()
        new = []
        for img, aud in zip(imgs, auds):
            p = PairItem(img, aud)
            p.update_duration()
            p.validate()
            new.append(p)
        self.model.add_pairs(new)
        self._update_counts()
        self._resize_columns()

    def _clear_all(self):
        if (
            QtWidgets.QMessageBox.question(
                self, "Löschen?", "Alle Paare wirklich entfernen?"
            )
            != QtWidgets.QMessageBox.Yes
        ):
            return
        self._push_history()
        self.model.clear()
        self.image_list.clear()
        self.audio_list.clear()
        self.log_edit.clear()
        self.dashboard.mini_log.clear()
        self._update_counts()

    def _undo_last(self):
        if not self._history:
            return
        last = self._history.pop()
        self.model.clear()
        self.model.add_pairs(last)
        self._update_counts()
        self._resize_columns()

    # ----- save / load -----
    def _save_project(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Projekt speichern", str(Path.cwd() / "projekt.json"), "JSON (*.json)"
        )
        if not path:
            return
        data = {
            "pairs": [
                {"image": p.image_path, "audio": p.audio_path, "output": p.output}
                for p in self.pairs
            ],
            "settings": self._gather_settings(),
        }
        Path(path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self._log(f"Projekt gespeichert: {path}")

    def _load_project(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Projekt laden", str(Path.cwd()), "JSON (*.json)"
        )
        if not path:
            return
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self._push_history()
        self.model.clear()
        new = []
        for d in data.get("pairs", []):
            p = PairItem(d.get("image", ""), d.get("audio"))
            p.output = d.get("output", "")
            p.update_duration()
            p.validate()
            new.append(p)
        self.model.add_pairs(new)
        s = data.get("settings", {})
        out_dir = s.get("out_dir", "")
        if out_dir == str(default_output_dir()):
            self.out_dir_edit.setText("")
        else:
            self.out_dir_edit.setText(out_dir)
        self.crf_spin.setValue(s.get("crf", self.crf_spin.value()))
        self.preset_combo.setCurrentText(
            s.get("preset", self.preset_combo.currentText())
        )
        self.width_spin.setValue(s.get("width", self.width_spin.value()))
        self.height_spin.setValue(s.get("height", self.height_spin.value()))
        abitrate = s.get("abitrate", "")
        if abitrate in ("", "192k"):
            self.abitrate_edit.setText("")
        else:
            self.abitrate_edit.setText(abitrate)
        self._update_counts()
        self._resize_columns()
        self._log(f"Projekt geladen: {path}")

    # ----- encode -----
    def _gather_settings(self) -> Dict[str, Any]:
        return {
            "out_dir": self.out_dir_edit.text().strip() or str(default_output_dir()),
            "crf": self.crf_spin.value(),
            "preset": self.preset_combo.currentText(),
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "abitrate": normalize_bitrate(self.abitrate_edit.text()),
        }

    def _start_encode(self):
        if not check_ffmpeg():
            QtWidgets.QMessageBox.critical(
                self,
                "FFmpeg fehlt",
                "FFmpeg oder ffprobe nicht gefunden. Bitte installieren.",
            )
            return
        if not self.pairs:
            QtWidgets.QMessageBox.information(
                self, "Keine Aufgaben", "Es sind keine Paare zum Verarbeiten vorhanden."
            )
            return
        if any(p.audio_path is None for p in self.pairs):
            QtWidgets.QMessageBox.warning(
                self, "Fehlende Audios", "Nicht alle Bilder haben ein Audio."
            )
            return
        for p in self.pairs:
            p.validate()
        invalid = [p for p in self.pairs if not p.valid]
        if invalid:
            QtWidgets.QMessageBox.critical(
                self, "Validierungsfehler", invalid[0].validation_msg
            )
            return
        self.btn_encode.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_total.setValue(0)
        self.dashboard.set_progress(0)
        self._log("Starte Encoding …")
        self.worker = EncodeWorker(self.pairs, self._gather_settings(), self.copy_only)
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.row_progress.connect(self._on_row_progress)
        self.worker.overall_progress.connect(self._on_overall_progress)
        self.worker.row_error.connect(self._on_row_error)
        self.worker.log.connect(self._log)
        self.worker.finished.connect(self._encode_finished)
        self.thread.start()

    def _stop_encode(self):
        if self.worker:
            self.worker.stop()
        self.btn_stop.setEnabled(False)

    def _on_row_progress(self, row: int, perc: float):
        if 0 <= row < len(self.pairs):
            self.pairs[row].progress = perc
            idx = self.model.index(row, 6)
            self.model.dataChanged.emit(idx, idx)

    def _on_overall_progress(self, perc: float):
        v = int(perc)
        self.progress_total.setValue(v)
        self.dashboard.set_progress(v)

    def _on_row_error(self, row: int, msg: str):
        self._log(f"Fehler in Zeile {row+1}: {msg}")
        if 0 <= row < len(self.pairs):
            self.pairs[row].status = "FEHLER"
            idx = self.model.index(row, 7)
            self.model.dataChanged.emit(idx, idx)
        self._update_counts()

    def _encode_finished(self):
        self.btn_encode.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_total.setValue(100)
        self.dashboard.set_progress(100)
        self._log("Alle Jobs abgeschlossen.")
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        self.thread = None
        self.worker = None
        self._update_counts()
        if self.clear_after.isChecked():
            self._clear_all()

    # ----- misc -----
    def _toggle_copy_mode(self, checked: bool):
        self.copy_only = checked
        self._log(
            f"Archivmodus: Dateien werden {'kopiert' if checked else 'verschoben'}."
        )

    def _global_exception(self, etype, value, tb):
        import traceback

        msg = "".join(traceback.format_exception(etype, value, tb))
        QtWidgets.QMessageBox.critical(self, "Unerwarteter Fehler", msg)
        self._log(msg)

    def _resize_columns(self):
        header = self.table.horizontalHeader()
        header.resizeSections(QHeaderView.ResizeToContents)

    def _show_selected_path(self):
        index = self.table.currentIndex()
        if not index.isValid():
            return
        if index.column() not in (2, 3, 5):
            index = index.siblingAtColumn(2)
        self._show_statusbar_path(index)

    def _show_statusbar_path(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return
        if index.column() in (2, 3, 5):
            self.statusBar().showMessage(self.model.data(index, Qt.DisplayRole), 5000)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.thread and self.thread.isRunning():
            reply = QtWidgets.QMessageBox.question(
                self,
                "Laufender Vorgang",
                "Es laufen noch Umwandlungen. Wirklich beenden?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if reply != QtWidgets.QMessageBox.Yes:
                event.ignore()
                return
            if self.worker:
                self.worker.stop()
            self.thread.quit()
            self.thread.wait()
            self.thread = None
            self.worker = None
        self._update_counts()
        self.settings.setValue("ui/geometry", self.saveGeometry())
        self.settings.setValue("ui/window_state", self.saveState())
        self.settings.setValue("ui/clear_after", self.clear_after.isChecked())
        self.settings.setValue("ui/show_thumbs", self.show_thumbs.isChecked())
        s = self._gather_settings()
        self.settings.setValue("encode/out_dir", s["out_dir"])
        self.settings.setValue("encode/crf", s["crf"])
        self.settings.setValue("encode/preset", s["preset"])
        self.settings.setValue("encode/width", s["width"])
        self.settings.setValue("encode/height", s["height"])
        self.settings.setValue("encode/abitrate", s["abitrate"])
        try:
            NOTES_FILE.write_text(self.notes_edit.toPlainText(), encoding="utf-8")
        except Exception as exc:
            logger.error("Notizen konnten nicht gespeichert werden: %s", exc)
        super().closeEvent(event)


# ---- Public
def run_gui():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    if QtWidgets.QApplication.instance() is app:
        sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
