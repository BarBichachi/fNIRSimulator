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
        self.data_generator = data_generator
        self.is_streaming = False
        self.lsl_outlet = None
        self.lsl_thread = None

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
        # Setup the LSL stream info
        info = StreamInfo(config.STREAM_NAME, config.STREAM_TYPE, 16, 50, 'float32', config.STREAM_ID)
        channels = info.desc().append_child("channels")
        for i in range(8):
            for wavelength in ['760nm', '850nm']:
                ch = channels.append_child("channel")
                ch.append_child_value("label", f"CH{i + 1}_{wavelength}")
                ch.append_child_value("type", "fNIRS")

        self.lsl_outlet = StreamOutlet(info)
        print("LSL stream started...")

        while self.is_streaming:
            sample = self.data_generator.generate_sample()
            self.lsl_outlet.push_sample(sample)
            time.sleep(1 / config.SAMPLE_RATE)  # Sleep to maintain the 50Hz sample rate

        self.lsl_outlet = None
        print("LSL stream stopped.")