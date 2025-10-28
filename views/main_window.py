from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton, QLabel, QButtonGroup)
from PySide6.QtCore import QTimer

import config
from logic.data_generator import DataGenerator
from logic.lsl_streamer import LSLStreamer
from views.optode_pad_widget import OptodePadWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_generator = DataGenerator()
        self.streamer = LSLStreamer(self.data_generator)
        self.ui_update_timer = QTimer(self)
        self.ui_update_timer.setInterval(1000 // config.UI_UPDATE_RATE_HZ)  # Update UI 10 times per second (10Hz)

        self.state_colors = {
            "Calm / Baseline": "#0288d1",  # Blue
            "Cognitive Load": "#ffa000",  # Orange
            "Artifact": "#5e35b1"  # Purple
        }
        self.setWindowTitle("fNIRS OctaMon Simulator")
        self.setGeometry(100, 100, 750, 650)
        self._apply_styles()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        main_layout.addWidget(self._create_stream_control_group())
        main_layout.addWidget(self._create_state_control_group())
        main_layout.addWidget(self._create_optode_view_group())

        self._connect_signals()
        self._update_current_state_label()  # Set initial state text

    def _create_stream_control_group(self):
        group = QGroupBox("Stream Control")
        layout = QHBoxLayout()
        self.status_label = QLabel(
            "Stream Status: <span style='color: #d32f2f; font-weight: bold;'>NOT STREAMING</span>")

        self.toggle_stream_button = QPushButton("Start Streaming")
        self.toggle_stream_button.setObjectName("startButton")  # Start with green style

        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.toggle_stream_button)
        group.setLayout(layout)
        return group

    def _create_state_control_group(self):
        group = QGroupBox("Simulation State")
        layout = QHBoxLayout()

        self.current_state_label = QLabel("Current State: <b>Calm / Baseline</b>")
        self.state_button_group = QButtonGroup(self)

        self.calm_button = self._create_state_button("Calm / Baseline", "calmButton")
        self.cognitive_button = self._create_state_button("Cognitive Load", "cognitiveButton")
        self.artifact_button = self._create_state_button("Artifact", "artifactButton")

        self.calm_button.setChecked(True)

        layout.addWidget(self.current_state_label)
        layout.addStretch()
        layout.addWidget(self.calm_button)
        layout.addWidget(self.cognitive_button)
        layout.addWidget(self.artifact_button)
        group.setLayout(layout)
        return group

    def _create_state_button(self, text, obj_name):
        """Helper to create and configure a state button."""
        button = QPushButton(text)
        button.setObjectName(obj_name)
        button.setCheckable(True)
        self.state_button_group.addButton(button)
        return button

    def _create_optode_view_group(self):
        group = QGroupBox("Live Optode View")
        layout = QHBoxLayout()

        left_hemi_group = QGroupBox("Left Hemisphere")
        left_hemi_layout = QVBoxLayout()
        self.left_pad = OptodePadWidget("L")
        left_hemi_layout.addWidget(self.left_pad)
        left_hemi_group.setLayout(left_hemi_layout)

        right_hemi_group = QGroupBox("Right Hemisphere")
        right_hemi_layout = QVBoxLayout()
        self.right_pad = OptodePadWidget("R")
        right_hemi_layout.addWidget(self.right_pad)
        right_hemi_group.setLayout(right_hemi_layout)

        #layout.addStretch(1)  # Add stretch before
        layout.addWidget(left_hemi_group)
        layout.addWidget(right_hemi_group)
        #layout.addStretch(1)  # Add stretch after
        group.setLayout(layout)
        return group

    def _connect_signals(self):
        """Connect button clicks to their handler functions."""
        self.toggle_stream_button.clicked.connect(self._toggle_streaming)
        self.state_button_group.buttonClicked.connect(self._update_current_state_label)
        self.ui_update_timer.timeout.connect(self._update_data_display)

    def _toggle_streaming(self):
        is_currently_streaming = self.toggle_stream_button.objectName() == "stopButton"

        if is_currently_streaming:
            # --- Logic for STOPPING ---
            self.streamer.stop()  # <<< CHANGE
            self.ui_update_timer.stop()
            self.status_label.setText(
                "Stream Status: <span style='color: #d32f2f; font-weight: bold;'>NOT STREAMING</span>")
            self.toggle_stream_button.setText("Start Streaming")
            self.toggle_stream_button.setObjectName("startButton")
        else:
            # --- Logic for STARTING ---
            self.streamer.start()  # <<< CHANGE
            self.ui_update_timer.start()
            self.status_label.setText(
                "Stream Status: <span style='color: #388e3c; font-weight: bold;'>STREAMING</span>")
            self.toggle_stream_button.setText("Stop Streaming")
            self.toggle_stream_button.setObjectName("stopButton")

        self.toggle_stream_button.style().unpolish(self.toggle_stream_button)
        self.toggle_stream_button.style().polish(self.toggle_stream_button)

    def _update_current_state_label(self):
        """Updates the state label and the background color of the state buttons."""
        checked_button = self.state_button_group.checkedButton()
        if not checked_button:
            return

        self.data_generator.restart_state_timer()

        # Update the label text and color
        state_text = checked_button.text()
        state_color = self.state_colors.get(state_text, "#333")
        self.current_state_label.setText(f"Current State: <b style='color: {state_color};'>{state_text}</b>")

        # Programmatically update button styles for clarity
        for button in self.state_button_group.buttons():
            if button.isChecked():
                # Set the specific color for the selected button
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.state_colors.get(button.text())};
                        color: white;
                        border: 1px solid #555;
                        border-radius: 5px; padding: 8px 16px; font-size: 14px;
                    }}
                """)
            else:
                # Reset the other buttons to the default gray style
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0; border: 1px solid #b0b0b0;
                        border-radius: 5px; padding: 8px 16px; font-size: 14px;
                    }
                    QPushButton:hover { background-color: #e9e9e9; }
                """)

    def _apply_styles(self):
        """Applies a consistent, visible stylesheet to the application."""
        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; color: #333; font-family: Arial; }
            QGroupBox {
                font: bold 14px; border: 1px solid #ccc; border-radius: 8px; margin-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px;
            }
            QLabel { font-size: 14px; }
            QPushButton {
                background-color: #e0e0e0; border: 1px solid #b0b0b0;
                border-radius: 5px; padding: 8px 16px; font-size: 14px;
            }
            QPushButton:hover { background-color: #e9e9e9; }
            QPushButton:disabled { background-color: #f5f5f5; color: #aaa; }

            /* --- Single Toggle Stream Button --- */
            QPushButton#startButton { background-color: #c8e6c9; } /* Light Green */
            QPushButton#stopButton { background-color: #ffcdd2; } /* Light Red */

            /* --- State Button Colors --- */
            QPushButton:checkable:checked#calmButton {
                background-color: #b3e5fc; border-color: #0288d1; /* Light Blue */
            }
            QPushButton:checkable:checked#cognitiveButton {
                background-color: #ffecb3; border-color: #ffa000; /* Light Orange */
            }
            QPushButton:checkable:checked#artifactButton {
                background-color: #d1c4e9; border-color: #5e35b1; /* Light Purple */
            }
        """)

    def _update_data_display(self):
        """Fetches a new sample from the generator and updates the UI."""
        # Set the generator's state based on which button is checked
        current_state = self.state_button_group.checkedButton().text()
        self.data_generator.set_state(current_state)

        # Generate one new sample of data
        sample = self.data_generator.generate_sample()

        # Update the UI pads with the new data
        self.left_pad.update_data(sample[0:4])
        self.right_pad.update_data(sample[4:8])