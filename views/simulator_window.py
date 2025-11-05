# views/main_window.py

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton, QLabel, QButtonGroup, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

import config
from logic.data_generator import DataGenerator
from logic.lsl_streamer import LSLStreamer
from views.optode_pad_widget import OptodePadWidget
from logic.file_loader import load_txt_file, parse_oxysoft_header
from views.file_info_dialog import show_file_info_dialog


class MainWindow(QMainWindow):
    # The main application window for the fNIRS Simulator.
    def __init__(self):
        super().__init__()

        # --- Application State ---
        self.app_state = 'live'  # 'live' or 'playback'

        # --- Backend Logic ---
        self.data_generator = DataGenerator()
        self.streamer = LSLStreamer(self.data_generator)

        # --- UI Timer ---
        self.ui_update_timer = QTimer(self)
        self.ui_update_timer.setInterval(1000 // config.UI_UPDATE_RATE_HZ)
        self.ui_update_timer.timeout.connect(self._update_data_display)

        self.state_colors = {
            "Calm / Baseline": "#0288d1",
            "Cognitive Load": "#ffa000",
            "Artifact": "#5e35b1"
        }

        self._init_ui()
        self._connect_signals()
        self._update_ui_for_state()  # Set initial UI state

    def _init_ui(self):
        # Initializes the UI elements for the simulator.
        self.setWindowTitle("fNIRS OctaMon Simulator")
        self.setGeometry(100, 100, 750, 650)
        self._apply_styles()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- File Control Group ---
        file_group = QGroupBox("File Control")
        file_layout = QHBoxLayout()
        self.load_file_button = QPushButton("Load File...")
        self.remove_file_button = QPushButton("Remove File")
        self.loaded_file_label = QLabel("Mode: Live Simulation")
        self.loaded_file_label.setStyleSheet("font-weight: bold;")
        file_layout.addWidget(self.load_file_button)
        file_layout.addWidget(self.remove_file_button)
        file_layout.addStretch()
        file_layout.addWidget(self.loaded_file_label)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # --- Stream Control Group ---
        stream_group = QGroupBox("Simulation Control")
        stream_layout = QHBoxLayout()
        self.status_label = QLabel("Status: <span style='color: red; font-weight: bold;'>NOT STREAMING</span>")
        self.toggle_stream_button = QPushButton("Start Streaming")
        self.toggle_stream_button.setObjectName("startButton")
        stream_layout.addWidget(self.status_label)
        stream_layout.addStretch()
        stream_layout.addWidget(self.toggle_stream_button)
        stream_group.setLayout(stream_layout)
        main_layout.addWidget(stream_group)

        # --- Simulation State Group ---
        self.state_group = QGroupBox("Simulation State")
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
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
        self.state_group.setLayout(layout)
        main_layout.addWidget(self.state_group)

        # --- Live Optode View Group ---
        optode_view_group = QGroupBox("Live Optode View (First 8 Channels)")
        optode_view_layout = QHBoxLayout()
        self.left_pad = OptodePadWidget("L")
        self.right_pad = OptodePadWidget("R")
        optode_view_layout.addWidget(self.left_pad)
        optode_view_layout.addWidget(self.right_pad)
        optode_view_group.setLayout(optode_view_layout)
        main_layout.addWidget(optode_view_group)

        main_layout.addStretch()

    def _create_state_button(self, text, obj_name):
        # Helper to create and configure a state button.
        button = QPushButton(text)
        button.setObjectName(obj_name)
        button.setCheckable(True)
        self.state_button_group.addButton(button)
        return button

    def _connect_signals(self):
        # Connects all UI signals to their handler methods.
        self.toggle_stream_button.clicked.connect(self._toggle_streaming)
        self.load_file_button.clicked.connect(self._load_file)
        self.remove_file_button.clicked.connect(self._remove_file)

        # --- Connect radio buttons to update the generator's state ---
        self.state_button_group.buttonClicked.connect(self._update_current_state_label)

    def _update_ui_for_state(self):
        # Updates the UI based on whether a file is loaded or not.
        if self.app_state == 'live':
            self.state_group.setEnabled(True)
            self.toggle_stream_button.setText("Start Streaming")
            self.remove_file_button.setEnabled(False)
            self.load_file_button.setEnabled(True)
            self.loaded_file_label.setText("Mode: <b>Live Simulation</b>")
        elif self.app_state == 'playback':
            self.state_group.setEnabled(False)
            self.toggle_stream_button.setText("Start Simulation")
            self.remove_file_button.setEnabled(True)
            self.load_file_button.setEnabled(False)

    def _load_file(self):
        # Opens a file dialog to load an OxySoft .txt file.
        filepath, _ = QFileDialog.getOpenFileName(self, "Open OxySoft TXT File", "", "Text Files (*.txt)")
        if not filepath:
            return

        metadata, data_start_line = parse_oxysoft_header(filepath)
        if metadata is None:
            QMessageBox.critical(self, "Error", "Could not parse file header. Is this a valid OxySoft TXT export?")
            return

        data, num_channels = load_txt_file(filepath, data_start_line)
        if data is None:
            QMessageBox.critical(self, "Error", "Could not load numerical data from file.")
            return

        # --- Show metadata to user ---
        show_file_info_dialog(self, filepath, metadata)

        # --- Configure backend ---
        self.data_generator.load_file_data(data, num_channels)
        self.streamer.set_sample_rate(metadata['Sample Rate'])

        self.app_state = 'playback'
        self.loaded_file_label.setText(f"Mode: <b>File Playback ({num_channels} streams)</b>")
        self._update_ui_for_state()

    def _remove_file(self):
        # Unloads the file and switches back to live simulation mode.
        self.data_generator.unload_file_data()
        self.streamer.set_sample_rate(config.SAMPLE_RATE)
        self.app_state = 'live'
        self._update_ui_for_state()

    def _toggle_streaming(self):
        # Starts or stops the LSL stream.
        if self.streamer.is_streaming:
            self.streamer.stop()
            self.ui_update_timer.stop()
            self.status_label.setText("Status: <span style='color: red; font-weight: bold;'>NOT STREAMING</span>")

            # --- Re-enable controls ---
            self._update_ui_for_state()
        else:
            self.streamer.start()
            self.ui_update_timer.start()
            self.status_label.setText("Status: <span style='color: green; font-weight: bold;'>STREAMING</span>")

            # --- Disable controls ---
            self.load_file_button.setEnabled(False)
            self.remove_file_button.setEnabled(False)
            self.toggle_stream_button.setText("Stop Simulation" if self.app_state == 'playback' else "Stop Streaming")

    def _update_current_state_label(self):
        # Updates the state label and the background color of the state buttons.
        checked_button = self.state_button_group.checkedButton()
        if not checked_button:
            return

        state_text = checked_button.text()
        self.data_generator.set_state(state_text)
        self.data_generator.restart_state_timer()  # Restart timer on click
        state_color = self.state_colors.get(state_text, "#333")
        self.current_state_label.setText(f"Current State: <b style='color: {state_color};'>{state_text}</b>")

        for button in self.state_button_group.buttons():
            if button.isChecked():
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.state_colors.get(button.text())};
                        color: white; border: 1px solid #555;
                        border-radius: 5px; padding: 8px 16px; font-size: 14px;
                    }}
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0; border: 1px solid #b0b0b0;
                        border-radius: 5px; padding: 8px 16px; font-size: 14px;
                    }
                    QPushButton:hover { background-color: #e9e9e9; }
                """)

    def _update_data_display(self):
        # Fetches a new sample from the generator and updates the UI.
        if not self.streamer.is_streaming:
            return

        # Get the next sample that will be streamed
        sample_data = self.data_generator.generate_sample()

        # We only display the first 8 channels (16 streams) on the UI
        # This works even if the file has 32 streams.
        ui_data = sample_data[:16]

        # Convert to a more "raw" looking value for the UI
        # We just take the 760nm wavelength (every 2nd value) for the 8-channel display
        display_values = [ui_data[i] for i in range(1, 16, 2)]

        if len(display_values) == 8:
            self.left_pad.update_data(display_values[0:4])
            self.right_pad.update_data(display_values[4:8])

    def closeEvent(self, event):
        # Ensures the stream is stopped when the window is closed.
        self.streamer.stop()
        event.accept()

    def _apply_styles(self):
        # Applies a consistent stylesheet to the application.
        # This is the user's requested style
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; color: #333; font-family: Arial; }
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