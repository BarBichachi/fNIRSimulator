import math

import numpy as np
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

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

        # Create the central receiver
        rx1 = OptodeWidget("Rx1", "#87ceeb")  # Sky Blue

        # Create transmitter-label pairs and place them
        tx1_pair = self._create_tx_pair(1, f"{self.hemisphere_prefix}1")
        tx2_pair = self._create_tx_pair(2, f"{self.hemisphere_prefix}2")
        tx3_pair = self._create_tx_pair(3, f"{self.hemisphere_prefix}3")
        tx4_pair = self._create_tx_pair(4, f"{self.hemisphere_prefix}4")

        # Place pairs and central receiver on the grid
        grid.addWidget(tx1_pair, 0, 0, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(tx2_pair, 0, 1, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(rx1, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)  # Span receiver across two columns
        grid.addWidget(tx4_pair, 2, 0, Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(tx3_pair, 2, 1, Qt.AlignmentFlag.AlignCenter)

    def _create_tx_pair(self, tx_num, channel_label_text):
        """Creates a container with a transmitter and its data label."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create the transmitter widget
        tx_widget = OptodeWidget(f"Tx{tx_num}", "#ffd700")  # Gold Yellow

        # Create the data labels
        channel_label = QLabel(channel_label_text)
        channel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        channel_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        # Two-line values row + small Rx badge to the right
        # First make a horizontal strip: [ values (VBox) | RX (badge) ]
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Two stacked lines for 850/760
        values_box = QWidget()
        values_v = QVBoxLayout(values_box)
        values_v.setContentsMargins(0, 0, 0, 0)
        values_v.setSpacing(2)
        l850 = QLabel("850nm: —")
        l850.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l850.setFont(QFont("Arial", 10))
        l760 = QLabel("760nm: —")
        l760.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l760.setFont(QFont("Arial", 10))
        values_v.addWidget(l850)
        values_v.addWidget(l760)
        h.addWidget(values_box)

        layout.addWidget(tx_widget)
        layout.addWidget(channel_label)
        layout.addLayout(h)

        # Keep refs for updates
        self.data_labels[tx_num] = {'l850': l850, 'l760': l760}

        return container

    def update_raw_channels(self, items):
        """
        items: list of 4 tuples -> (i850: float|nan, i760: float|nan)
        """
        for idx, pair in enumerate(items):
            tx_num = idx + 1
            if tx_num not in self.data_labels:
                continue
            i850, i760 = pair if pair and len(pair) == 2 else (float("nan"), float("nan"))

            def fmt(v):
                return "—" if v is None or not np.isfinite(v) else f"{v:.3f}"

            lbls = self.data_labels[tx_num]
            lbls['l850'].setText(f"850nm: {fmt(i850)}")
            lbls['l760'].setText(f"760nm: {fmt(i760)}")