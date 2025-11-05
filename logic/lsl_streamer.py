import threading
import time
from pylsl import StreamInfo, StreamOutlet
import config
from logic.data_generator import DataGenerator


class LSLStreamer:
    """
    Manages the LSL data stream in a separate thread.
    """

    def __init__(self, data_generator: DataGenerator):
        # Initializes the LSLStreamer.
        self.data_generator = data_generator
        self.is_streaming = False
        self.lsl_outlet = None
        self.lsl_thread = None
        self.sample_rate = config.SAMPLE_RATE  # Default to config's live rate

    def set_sample_rate(self, rate):
        """Sets the streaming sample rate (e.g., 10Hz from file)."""
        self.sample_rate = rate
        print(f"LSLStreamer: Sample rate set to {rate} Hz")

    def start(self):
        """Starts the LSL streaming thread."""
        if self.is_streaming:
            return
        self.is_streaming = True
        self.lsl_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.lsl_thread.start()

    def stop(self):
        """Stops the LSL streaming thread."""
        self.is_streaming = False
        if self.lsl_thread:
            self.lsl_thread.join()  # Wait for the thread to finish cleanly

    def _stream_loop(self):
        """The main loop for generating and pushing data to LSL."""
        # --- Get channel count from generator (16 or 32) ---
        num_channels = self.data_generator.num_channels

        # --- Setup the LSL stream info dynamically ---
        info = StreamInfo(config.STREAM_NAME, config.STREAM_TYPE, num_channels, self.sample_rate, 'float32',
                          config.STREAM_ID)
        channels = info.desc().append_child("channels")

        num_physical_channels = num_channels // 2
        for i in range(num_physical_channels):
            ch_name = f"CH{i + 1}"
            # This labeling is assumed, but standard for 2 wavelengths
            channels.append_child("channel").append_child_value("label", f"{ch_name}_760nm")
            channels.append_child("channel").append_child_value("label", f"{ch_name}_850nm")

        self.lsl_outlet = StreamOutlet(info)
        print(f"LSL stream started with {num_channels} channels at {self.sample_rate} Hz...")

        while self.is_streaming:
            sample = self.data_generator.generate_sample()
            self.lsl_outlet.push_sample(sample)

            # --- Maintain correct sample rate ---
            time.sleep(1 / self.sample_rate)

        print("LSL stream stopped.")