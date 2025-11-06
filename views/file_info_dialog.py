from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QApplication
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize
import os
import textwrap


def show_file_info_dialog(parent, filepath, metadata):
    """
    Displays a styled modal dialog with the metadata extracted from the loaded file.
    """
    def val(key, suffix=""):
        v = metadata.get(key, "N/A")
        return f"{v}{suffix}" if (v != "N/A" and suffix) else str(v)

    # --------- Build plain-text summary for console ----------
    plain = textwrap.dedent(f"""\
        --- File Loaded: {os.path.basename(filepath)} ---
        Acquisition
          Start Time   : {val('Start of Measurement')}
          Duration     : {val('Duration (s)', ' s')}
          Sample Rate  : {val('Sample Rate', ' Hz')}
        -----------------------------------------------
        Optode Setup
          Template     : {val('Optode Template')}
          Distance     : {val('Optode Distance (mm)', ' mm')}
          DPF          : {val('DPF')}
        -----------------------------------------------
        Device
          Device ID    : {val('Device ID')}
          Receivers    : {val('# Receivers')}
          Light Sources: {val('# Light Sources')}
        """)
    print(plain)

    # --------- Dialog scaffold ----------
    dlg = QDialog(parent)
    dlg.setWindowTitle(f"File Loaded · {os.path.basename(filepath)}")
    dlg.setModal(True)
    dlg.setMinimumWidth(520)
    dlg.setWindowIcon(QIcon.fromTheme("document-open"))

    root = QVBoxLayout(dlg)
    root.setContentsMargins(18, 18, 18, 18)
    root.setSpacing(14)

    # --------- Header (icon + filename + path) ----------
    header = QHBoxLayout()
    icon_label = QLabel()
    icon = QIcon.fromTheme("text-x-generic")
    if icon.isNull():
        icon = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_FileIcon)
    pix = icon.pixmap(QSize(28, 28))
    icon_label.setPixmap(pix)

    title_box = QVBoxLayout()
    title_lbl = QLabel(os.path.basename(filepath))
    title_lbl.setObjectName("title")
    title_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    path_lbl = QLabel(os.path.abspath(filepath))
    path_lbl.setObjectName("subtle")
    path_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    title_box.addWidget(title_lbl)
    title_box.addWidget(path_lbl)

    header.addWidget(icon_label)
    header.addLayout(title_box)
    header.addStretch(1)
    root.addLayout(header)

    # --- Helpers ---
    def section_caption(text: str) -> QLabel:
        cap = QLabel(text)
        cap.setObjectName("section")
        return cap

    def hr() -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def grid_rows(pairs):
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        grid.setContentsMargins(0, 0, 0, 0)
        for row, (k, v) in enumerate(pairs):
            k_lbl = QLabel(k)
            k_lbl.setObjectName("key")
            v_lbl = QLabel(v)
            v_lbl.setObjectName("val")
            v_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            grid.addWidget(k_lbl, row, 0, Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(v_lbl, row, 1, Qt.AlignmentFlag.AlignLeft)
        return grid

    # --------- Sections ----------
    # Acquisition
    root.addWidget(section_caption("Acquisition"))
    root.addLayout(grid_rows([
        ("Start Time",   val("Start of Measurement")),
        ("Duration",     val("Duration (s)", " s")),
        ("Sample Rate",  val("Sample Rate", " Hz")),
    ]))
    root.addWidget(hr())

    # Optode setup
    root.addWidget(section_caption("Optode Setup"))
    root.addLayout(grid_rows([
        ("Template",     val("Optode Template")),
        ("Distance",     val("Optode Distance (mm)", " mm")),
        ("DPF",          val("DPF")),
    ]))
    root.addWidget(hr())

    # Device
    root.addWidget(section_caption("Device"))
    root.addLayout(grid_rows([
        ("Device ID",     val("Device ID")),
        ("Receivers",     val("# Receivers")),
        ("Light Sources", val("# Light Sources")),
    ]))

    # --- OK button ---
    buttons = QHBoxLayout()
    buttons.addStretch(1)
    ok_btn = QPushButton("OK")
    ok_btn.setDefault(True)
    ok_btn.clicked.connect(dlg.accept)
    buttons.addWidget(ok_btn)
    root.addLayout(buttons)

    # --------- Styling ----------
    dlg.setStyleSheet("""
        QDialog {
            background-color: #f6f6f6; /* Light gray */
        }
        QLabel {
            color: #000000;
            background: transparent;
        }
        QLabel#title {
            font-weight: 600;
            font-size: 16px;
        }
        QLabel#subtle {
            color: #555555;
            font-size: 10px;
        }
        QLabel#section {
            margin-top: 6px;
            font-weight: 600;
            color: #000000;
        }
        QLabel#key {
            color: #333333;
            min-width: 130px;
        }
        QLabel#val {
            color: #000000;
            font-weight: 500;
        }
        QFrame[frameShape="4"] { /* HLine */
            color: #cccccc;
            margin: 6px 0px 6px 0px;
        }
        QPushButton {
            padding: 6px 12px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background: #e0e0e0;
        }
        QPushButton:default {
            font-weight: 600;
        }
        """)

    dlg.exec()