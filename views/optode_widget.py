from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class OptodeWidget(QWidget):
    """
    A reusable widget to display a single styled optode circle.
    """

    def __init__(self, label_text, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)

        self.label = QLabel(label_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 10, QFont.Bold))

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        # This stylesheet is crucial for the circular appearance
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: 2px solid #555555;
                border-radius: 30px; /* This MUST be half the width/height */
                color: black;
            }}
        """)