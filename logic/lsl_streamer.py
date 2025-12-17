import threading
import time
from pylsl import StreamInfo, StreamOutlet, local_clock
import config
from logic.data_generator import DataGenerator


class LSLStreamer:
    """ Manages the LSL data stream in a separate thread. """
    def __init__(self, data_generator: DataGenerator):
        # Initializes the LSLStreamer.
        self.data_generator = data_generator
        self.is_streaming = False
        self.lsl_outlet = None
        self.lsl_thread = None
        self.sample_rate = config.SAMPLE_RATE  # Default to config's live rate
        self.last_sample = None  # UI reads this (do not advance generator in UI)
        self.samples_sent = 0

    def set_sample_rate(self, rate):
        """Sets the streaming sample rate (e.g., 10Hz from file)."""
        self.sample_rate = float(rate)
        print(f"LSLStreamer: Sample rate set to {self.sample_rate} Hz")

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
        # Get channel count from generator (e.g., 32 for 16 channels × 2 wavelengths).
        num_channels = len(config.LSL_CHANNEL_LABELS)

        # Setup the LSL stream info dynamically.
        info = StreamInfo(config.STREAM_NAME, config.STREAM_TYPE, num_channels, self.sample_rate, 'float32', config.STREAM_ID)

        # Add basic channel metadata for wavelengths.
        channels = info.desc().append_child("channels")
        for lbl in config.LSL_CHANNEL_LABELS:
            channels.append_child("channel").append_child_value("label", lbl)

        self.lsl_outlet = StreamOutlet(info)
        print(f"LSL stream started with {num_channels} channels at {self.sample_rate} Hz...")

        rate = max(0.0001, float(self.sample_rate))
        period = 1.0 / rate
        next_t = time.perf_counter()

        while self.is_streaming:
            next_t += period

            sample = self.data_generator.generate_sample()
            self.last_sample = sample
            self.lsl_outlet.push_sample(sample, local_clock())
            self.samples_sent += 1

            now = time.perf_counter()
            remaining = next_t - now
            if remaining > 0:
                time.sleep(remaining)
            else:
                # We're behind; resync to avoid drift runaway
                next_t = now

        print("LSL stream stopped.")