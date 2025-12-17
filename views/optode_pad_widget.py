import numpy as np
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import config
from views.optode_widget import OptodeWidget


class OptodePadWidget(QWidget):
    def __init__(self, hemisphere_prefix, parent=None):
        super().__init__(parent)
        self.hemisphere_prefix = hemisphere_prefix
        self.data_labels = {}
        self._init_ui()

    def _init_ui(self):
        grid = QGridLayout(self)
        grid.setSpacing(20)

        # --- 1. Determine Rx Name and Tx Offset based on Hemisphere ---
        if self.hemisphere_prefix == "L":
            rx_name = "Rx1"
            tx_offset = 0  # Left uses Tx1, Tx2, Tx3, Tx4
        else:
            rx_name = "Rx2"
            tx_offset = 4  # Right uses Tx5, Tx6, Tx7, Tx8

        # Create the central receiver
        rx_widget = OptodeWidget(rx_name, "#87ceeb")  # Sky Blue

        # Create transmitter-label pairs
        # We add the offset to the tx_num (e.g., 1+4 = 5 for Right side)
        tx1_pair = self._create_tx_pair(1 + tx_offset, f"{self.hemisphere_prefix}1")
        tx2_pair = self._create_tx_pair(2 + tx_offset, f"{self.hemisphere_prefix}2")
        tx3_pair = self._create_tx_pair(3 + tx_offset, f"{self.hemisphere_prefix}3")
        tx4_pair = self._create_tx_pair(4 + tx_offset, f"{self.hemisphere_prefix}4")

        # Place pairs and central receiver on the grid
        # Layout:
        # TxA  TxB
        #    Rx
        # TxD  TxC
        grid.addWidget(tx1_pair, 0, 0, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(tx2_pair, 0, 1, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(rx_widget, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)  # Span receiver
        grid.addWidget(tx4_pair, 2, 0, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(tx3_pair, 2, 1, Qt.AlignmentFlag.AlignCenter)

    def _create_tx_pair(self, tx_num, channel_label_text):
        # Creates a container with a transmitter and its OD(850/760) labels
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tx_widget = OptodeWidget(f"Tx{tx_num}", "#ffd700")

        channel_label = QLabel(channel_label_text)
        channel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        channel_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        l850 = QLabel("OD 850: —")
        l850.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l850.setFont(QFont("Arial", 10))
        l850.setStyleSheet("color: #e0e0e0;")

        l760 = QLabel("OD 760: —")
        l760.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l760.setFont(QFont("Arial", 10))
        l760.setStyleSheet("color: #e0e0e0;")

        layout.addWidget(tx_widget)
        layout.addWidget(channel_label)
        layout.addWidget(l850)
        layout.addWidget(l760)

        self.data_labels[tx_num] = {'l850': l850, 'l760': l760}
        return container

    def update_raw_channels(self, items):
        # items: list of 4 tuples -> (od850, od760)
        tx_offset = 0 if self.hemisphere_prefix == "L" else 4

        def fmt(v):
            if v is None or not np.isfinite(v):
                return "—"
            if abs(float(v) - float(config.PLACEHOLDER_HI)) <= float(config.PLACEHOLDER_EPS):
                return "—"
            return f"{float(v):.5f}"

        for idx, pair in enumerate(items):
            tx_num = idx + 1 + tx_offset
            if tx_num not in self.data_labels:
                continue

            od850, od760 = pair if pair and len(pair) == 2 else (float("nan"), float("nan"))
            lbls = self.data_labels[tx_num]
            lbls['l850'].setText(f"OD 850: {fmt(od850)}")
            lbls['l760'].setText(f"OD 760: {fmt(od760)}")

