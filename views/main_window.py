import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPushButton, QLabel, QButtonGroup, QFileDialog, QMessageBox, QFrame, QStyle, QSlider
)
from PySide6.QtCore import Qt, QTimer

import config
from logic.data_generator import DataGenerator
from logic.lsl_streamer import LSLStreamer
from views.optode_pad_widget import OptodePadWidget
from logic.file_loader import load_txt_file, parse_oxysoft_header
from views.file_info_dialog import show_file_info_dialog
from views.stylesheet import get_stylesheet


class MainWindow(QMainWindow):
    # The main application window for the fNIRS Simulator.
    def __init__(self):
        super().__init__()

        # --- Application State ---
        self.app_state = 'live'  # 'live' or 'playback'
        self.was_playing_before_drag = False

        # --- Backend Logic ---
        self.data_generator = DataGenerator()
        self.streamer = LSLStreamer(self.data_generator)

        # --- UI Timer ---
        self.ui_update_timer = QTimer(self)
        self.ui_update_timer.setInterval(1000 // config.UI_UPDATE_RATE_HZ)
        self.ui_update_timer.timeout.connect(self._update_data_display)

        self.state_colors = {
            "Calm": "#0288d1",
            "Cognitive Load": "#ffa000",
            "Artifact": "#5e35b1"
        }

        self._init_ui()
        self._connect_signals()
        self._update_ui_for_state()

    def _init_ui(self):
        # Initializes the UI elements for the simulator.
        self.setWindowTitle("fNIRS OctaMon Simulator")
        self.setStyleSheet(get_stylesheet())

        central_widget = QWidget(self)
        central_widget.setObjectName("MainBackground")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.setFixedWidth(700)
        QTimer.singleShot(0, self._center_on_screen)

        # --- File Control Group ---
        file_group = QGroupBox("File Control")
        file_layout = QHBoxLayout()

        self.load_file_button = QPushButton("Load File")
        self.remove_file_button = QPushButton("Remove File")
        self.mode_label = QLabel()

        file_layout.addWidget(self.load_file_button)
        file_layout.addWidget(self.remove_file_button)
        file_layout.addStretch()
        file_layout.addWidget(self.mode_label)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # --- Stream Control Group ---
        stream_group = QGroupBox("Simulation Control")
        stream_layout = QHBoxLayout()

        self.status_label = QLabel()
        self._set_status_label("NOT STREAMING", "red")

        self.toggle_stream_button = QPushButton("Start Streaming")
        self.toggle_stream_button.setObjectName("PrimaryButton")

        stream_layout.addWidget(self.status_label)
        stream_layout.addStretch()
        stream_layout.addWidget(self.toggle_stream_button)
        stream_group.setLayout(stream_layout)
        main_layout.addWidget(stream_group)

        # --- Playback Control Group ---
        self.playback_group = QGroupBox("Playback Control")
        self.playback_group.setVisible(False)
        playback_layout = QHBoxLayout()

        # Play/Pause Toggle Button
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setObjectName("PrimaryButton")
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_btn.setFixedSize(40, 30)
        self.play_pause_btn.setCheckable(True)

        # Stop Button
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.setFixedSize(40, 30)

        # Time Labels
        self.lbl_current_time = QLabel("00:00:00")
        self.lbl_total_time = QLabel("00:00:00")

        # Slider
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 100)

        playback_layout.addWidget(self.stop_btn)
        playback_layout.addWidget(self.play_pause_btn)
        playback_layout.addWidget(self.lbl_current_time)
        playback_layout.addWidget(self.seek_slider)
        playback_layout.addWidget(self.lbl_total_time)

        self.playback_group.setLayout(playback_layout)
        main_layout.addWidget(self.playback_group)

        # --- Simulation State Group ---
        self.state_group = QGroupBox("Simulation State")
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.current_state_label = QLabel()
        self.state_button_group = QButtonGroup(self)
        self.calm_button = self._create_state_button("Calm", "calmButton")
        self.cognitive_button = self._create_state_button("Cognitive Load", "cognitiveButton")
        self.artifact_button = self._create_state_button("Artifact", "artifactButton")
        self.state_button_group.setExclusive(True)
        self.calm_button.setChecked(True)

        layout.addWidget(self.current_state_label)
        layout.addStretch()
        layout.addWidget(self.calm_button)
        layout.addWidget(self.cognitive_button)
        layout.addWidget(self.artifact_button)
        self.state_group.setLayout(layout)
        main_layout.addWidget(self.state_group)

        # --- Live Optode View Group ---
        optode_view_group = QGroupBox("Live Optode View")
        optode_view_layout = QHBoxLayout()

        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setFrameShadow(QFrame.Shadow.Sunken)

        self.left_pad = OptodePadWidget("L")
        self.right_pad = OptodePadWidget("R")
        optode_view_layout.addWidget(self.left_pad)
        optode_view_layout.addWidget(vline)
        optode_view_layout.addWidget(self.right_pad)
        optode_view_group.setLayout(optode_view_layout)
        main_layout.addWidget(optode_view_group)

        main_layout.addStretch()
        QTimer.singleShot(0, self._update_current_state_label)

    def _center_on_screen(self):
        # Fit to content first (so we center the final size)
        self.adjustSize()
        geo = self.frameGeometry()
        geo.moveCenter(self.screen().availableGeometry().center())
        self.move(geo.topLeft())

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

        # Connect radio buttons to update the generator's state
        self.state_button_group.buttonClicked.connect(self._update_current_state_label)

        # Playback specific signals
        self.play_pause_btn.clicked.connect(self._toggle_playback_state)
        self.stop_btn.clicked.connect(self._stop_playback)

        # Handle seeking (User drags slider)
        self.seek_slider.sliderMoved.connect(self._on_slider_seek)
        self.seek_slider.sliderPressed.connect(self._on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self._on_slider_released)

    def _format_time(self, seconds):
        """Converts raw seconds to HH:MM:SS format."""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

    def _update_ui_for_state(self):
        # Updates visibility of controls based on app_state (live/playback).
        if self.app_state == 'live':
            self.state_group.setVisible(True)
            self.playback_group.setVisible(False)
            self.toggle_stream_button.setVisible(True)
            self.toggle_stream_button.setText("Start Streaming")
            self.remove_file_button.setEnabled(False)
            self.load_file_button.setEnabled(True)
            self._set_mode_label("Live Simulation", "#0288d1")

        elif self.app_state == 'playback':
            self.state_group.setVisible(False)
            self.playback_group.setVisible(True)
            self.toggle_stream_button.setVisible(False)
            self.remove_file_button.setEnabled(True)
            self.load_file_button.setEnabled(False)
            self._set_mode_label("File Playback", "#4CAF50")

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

        # Show metadata to user
        show_file_info_dialog(self, os.path.basename(filepath), metadata)

        # Setup backend
        self.data_generator.load_file_data(data, num_channels)
        self.streamer.set_sample_rate(metadata['Sample Rate'])

        # Setup Playback UI
        total_seconds = metadata['Duration (s)']
        total_samples = self.data_generator.get_total_samples()

        self.lbl_total_time.setText(self._format_time(total_seconds))
        self.seek_slider.setRange(0, total_samples)
        self.seek_slider.setValue(0)

        self.app_state = 'playback'
        self._update_ui_for_state()

    def _remove_file(self):
        # Unloads the file and switches back to live simulation mode.
        self._stop_playback()
        self.data_generator.unload_file_data()
        self.streamer.set_sample_rate(config.SAMPLE_RATE)
        self.app_state = 'live'
        self._update_ui_for_state()

    def _toggle_streaming(self):
        # Starts or stops the LSL stream.
        if self.streamer.is_streaming:
            self.streamer.stop()
            self.ui_update_timer.stop()
            self._set_status_label("NOT STREAMING", "red")
            self.toggle_stream_button.setText("Start Streaming")
            self.load_file_button.setEnabled(True)
        else:
            self.streamer.start()
            self.ui_update_timer.start()
            self._set_status_label("STREAMING", "green")
            self.toggle_stream_button.setText("Stop Streaming")
            self.load_file_button.setEnabled(False)

    def _update_current_state_label(self):
        # Updates the state label and the background color of the state buttons.
        checked_button = self.state_button_group.checkedButton()
        if not checked_button:
            return

        state_text = checked_button.text()
        self.data_generator.set_state(state_text)
        self.data_generator.restart_state_timer()

        # Get color for the active state
        active_color = self.state_colors.get(state_text, "#333")

        # 1. Update the Text Label
        self._set_state_label(state_text, active_color)

        # 2. Update Button Styles (Radio Behavior)
        for button in self.state_button_group.buttons():
            btn_text = button.text()
            btn_color = self.state_colors.get(btn_text, "#333")

            if button.isChecked():
                # Active Button: Colored background, White text
                button.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {btn_color};
                                color: white;
                                border: 1px solid {btn_color};
                                font-weight: bold;
                            }}
                        """)
            else:
                # Inactive Button: Dark background, Grey text
                button.setStyleSheet("""
                            QPushButton {
                                background-color: #252a33;
                                color: #e0e0e0;
                                border: 1px solid #303641;
                            }
                            QPushButton:hover {
                                background-color: #2c323d;
                            }
                        """)

    def _update_data_display(self):
        # Update UI once per tick while streaming
        if not self.streamer.is_streaming:
            return

        # Get the next sample that will be streamed
        sample = self.data_generator.generate_sample()

        # --- Update Playback UI if in playback mode ---
        if self.app_state == 'playback':
            cur_idx, total = self.data_generator.get_playback_status()
            rate = self.streamer.sample_rate or 1

            # Update Slider (Block signals to prevent loop)
            self.seek_slider.blockSignals(True)
            self.seek_slider.setValue(cur_idx)
            self.seek_slider.blockSignals(False)

            # Update Time Label
            current_seconds = cur_idx / rate
            self.lbl_current_time.setText(self._format_time(current_seconds))

            # Auto-stop if end reached
            if cur_idx >= total - 1:
                self._stop_playback()

        #  Build pad payloads: each item = (i850, i760) for 4 channels
        def to_pairs(chunk16):
            # chunk16 = 16 numbers = 8 streams = 4 channels × (850,760) FOR THIS PAD
            return [(chunk16[2 * i], chunk16[2 * i + 1]) for i in range(4)]

        if len(sample) >= 32:
            rx1 = sample[0:16]  # receiver 1 → left pad
            rx2 = sample[16:32]  # receiver 2 → right pad
            left_items = to_pairs(rx1)
            right_items = to_pairs(rx2)
        elif len(sample) == 16:
            # Single-receiver data: show on left; clear right
            rx = sample[0:16]
            left_items = to_pairs(rx)
            right_items = [(float('nan'), float('nan'))] * 4
        else:
            # Unexpected width; skip this tick safely
            return

        # Update pads
        self.left_pad.update_raw_channels(left_items)
        self.right_pad.update_raw_channels(right_items)

    def closeEvent(self, event):
        # Ensures the stream is stopped when the window is closed.
        self.streamer.stop()
        event.accept()

    # --- Playback Mode Controls ---
    def _toggle_playback_state(self):
        """Called by Play/Pause Button"""
        should_play = self.play_pause_btn.isChecked()

        if should_play:
            self.streamer.start()
            self.ui_update_timer.start()
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self._set_status_label("PLAYING", "green")
        else:
            self.streamer.stop()
            self.ui_update_timer.stop()
            self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            self._set_status_label("PAUSED", "orange")

    def _stop_playback(self):
        """Stops streaming and resets index to 0."""
        self.streamer.stop()
        self.ui_update_timer.stop()

        # Reset Logic
        self.data_generator.set_playback_index(0)

        # Reset UI
        self.play_pause_btn.setChecked(False)
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.seek_slider.setValue(0)
        self.lbl_current_time.setText("00:00:00")
        self._set_status_label("STOPPED", "red")

    # --- Slider Logic ---
    def _on_slider_pressed(self):
        """Pause playback when user grabs the slider."""
        self.was_playing_before_drag = self.streamer.is_streaming

        if self.was_playing_before_drag:
            self.streamer.stop()
            self.ui_update_timer.stop()

    def _on_slider_seek(self, value):
        # Update generator index
        self.data_generator.set_playback_index(value)

        # Update Time Label immediately while dragging
        rate = self.streamer.sample_rate or 1
        current_seconds = value / rate
        self.lbl_current_time.setText(self._format_time(current_seconds))

    def _on_slider_released(self):
        """Resume playback if it was playing before drag."""
        if self.was_playing_before_drag:
            self.streamer.start()
            self.ui_update_timer.start()
        self.was_playing_before_drag = False

    def _set_status_label(self, status_text, color):
        """Helper to format status label with consistent styling."""
        self.status_label.setText(f"Status: <span style='color: {color}; font-weight: bold;'>{status_text}</span>")

    def _set_mode_label(self, mode_text, color):
        """Helper to format mode label with consistent styling."""
        self.mode_label.setText(f"Mode: <span style='color: {color}; font-weight: bold;'>{mode_text}</span>")

    def _set_state_label(self, state_text, color):
        """Helper to format state label with consistent styling."""
        self.current_state_label.setText(f"State: <span style='color: {color}; font-weight: bold;'>{state_text}</span>")


        # FIX STATE LABEL MODE LABEL