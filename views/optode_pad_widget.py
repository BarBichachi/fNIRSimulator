from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
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
        layout.setAlignment(Qt.AlignCenter)

        # Create the transmitter widget
        tx_widget = OptodeWidget(f"Tx{tx_num}", "#ffd700")  # Gold Yellow

        # Create the data labels
        channel_label = QLabel(channel_label_text)
        channel_label.setAlignment(Qt.AlignCenter)
        channel_label.setFont(QFont("Arial", 9, QFont.Bold))

        value_label = QLabel("-.---")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 10))

        # Add widgets to the container's layout
        layout.addWidget(tx_widget)
        layout.addWidget(channel_label)
        layout.addWidget(value_label)

        # Store a reference for future data updates
        self.data_labels[tx_num] = value_label

        return container

    def update_data(self, data_values):
        """Updates the numerical data labels with new values."""
        for i, value in enumerate(data_values):
            channel_num = i + 1
            if channel_num in self.data_labels:
                # Format the raw intensity value as an integer
                self.data_labels[channel_num].setText(f"{int(value)}")