import time
import numpy as np
import math
import config


class DataGenerator:
    # Generates data, either simulated or from a file.
    def __init__(self):
        # Initializes the DataGenerator.
        self.start_time = time.time()
        self.state = "Calm / Baseline"
        self.state_start_time = self.start_time

        # --- File Playback Properties ---
        self.file_data = None
        self.playback_index = 0
        self.num_channels = config.NUM_CHANNELS

        # --- Per-channel personality (for 8 physical channels) ---
        # Slightly different oscillation freq, phase, amplitude and HRF gain
        self.channel_freq = np.linspace(1.0, 1.6, 8)          # Hz
        self.channel_phase = np.linspace(0.0, math.pi, 8)     # radians
        self.channel_gain = np.linspace(0.8, 1.2, 8)          # noise amplitude
        self.channel_hrf_gain = np.linspace(0.6, 1.4, 8)      # HRF sensitivity

    def set_state(self, new_state):
        """Updates the current simulation state."""
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = time.time()

    def restart_state_timer(self):
        """Forces the internal timer for the current state to reset."""
        self.state_start_time = time.time()

    def load_file_data(self, data, num_channels):
        """Loads file data (rows of 16 or 32 values). Controller should also set LSL rate from header."""
        self.file_data = np.asarray(data, dtype=float)
        self.num_channels = int(num_channels)
        self.playback_index = 0
        print(f"DataGenerator: Loaded file data with {self.num_channels} channels.")

    def unload_file_data(self):
        # Clears the file data and resets to default.
        self.file_data = None
        self.playback_index = 0
        self.num_channels = config.NUM_CHANNELS
        print("DataGenerator: Unloaded file data. Reverting to live simulation (32 raw channels).")

    def get_playback_status(self):
        """Returns the current playback index and total samples."""
        if self.file_data is not None:
            return self.playback_index, len(self.file_data)
        return 0, 0

    def _generate_live_sample(self):
        """Generate one live raw sample: 32 values = (Rx1 8 pairs + Rx2 8 pairs) × (850,760)."""
        t = time.time() - self.start_time
        st = time.time() - self.state_start_time
        freq_variation = [1.2 + i * 0.05 for i in range(8)]

        # State-dependent offset (HRF or artifacts)
        signal_offset_base  = 0.0
        if self.state == "Cognitive Load":
            cycle = st % 30.0
            if cycle < 20.0:
                signal_offset_base  = self._generate_hrf_shape(cycle) * config.HRF_SCALE
        elif self.state == "Artifact":
            if (st % 4.0) < 1.0:
                signal_offset_base  = np.random.uniform(-config.ARTIFACT_SCALE, config.ARTIFACT_SCALE)

        base_I = config.BASE_INTENSITY

        def make_rx(rx_bias: float, rx_index: int):
            out = []
            for ch in range(8):  # 8 physical channels
                # Per-channel parameters
                freq = self.channel_freq[ch]
                phase = self.channel_phase[ch] + rx_index * 0.3  # small extra phase per receiver
                gain = self.channel_gain[ch]
                hrf_gain = self.channel_hrf_gain[ch]

                # small physiological baseline oscillation (per-channel)
                base_noise = (
                        config.NOISE_A * gain * math.sin(2 * math.pi * freq * t + phase) +
                        config.NOISE_B * math.sin(2 * math.pi * 0.25 * t + phase * 0.3)
                )

                # Per-channel state offset
                local_offset = signal_offset_base * hrf_gain

                # For artifacts, add a bit of extra random per-channel wiggle
                if self.state == "Artifact" and signal_offset_base != 0.0:
                    jitter = np.random.uniform(-config.ARTIFACT_SCALE, config.ARTIFACT_SCALE)
                    local_offset += jitter * (0.5 + 0.5 * gain)

                # random sensor jitter
                eps = np.random.normal(0.0, config.JITTER_STD)

                i850 = (
                                   base_I + rx_bias + base_noise + eps + 0.4 * local_offset) * config.WL850_GAIN + config.WL850_BIAS
                i760 = (
                                   base_I + rx_bias + base_noise + eps - 1.0 * local_offset) * config.WL760_GAIN + config.WL760_BIAS

                # order: (850, 760)
                out.extend([i850, i760])

            return out

        # Two healthy receivers with a tiny offset so they differ slightly
        rx1 = make_rx(0.000, 0)   # receiver 1
        rx2 = make_rx(0.005, 1)   # receiver 2

        return rx1 + rx2  # 32 values

    def _generate_playback_sample(self):
        """Return next row from file, converting to raw-like intensity if needed."""
        if self.file_data is None:
            return [0.0] * self.num_channels

        row = self.file_data[self.playback_index]
        self.playback_index = (self.playback_index + 1) % len(self.file_data)

        return row[: self.num_channels]

    def generate_sample(self):
        # Generates a sample based on the current mode (live or playback).
        if self.file_data is not None:
            return self._generate_playback_sample()
        else:
            return self._generate_live_sample()

    def _generate_hrf_shape(self, t):
        # Generates a canonical Hemodynamic Response Function shape.
        n, lambda_val = 5, 1.5
        hrf = (t ** (n - 1) * np.exp(-t / lambda_val)) / (lambda_val ** n * math.factorial(n - 1))
        return hrf * config.HRF_SCALE

    def get_total_samples(self):
        """Returns the total number of samples in the loaded file."""
        return len(self.file_data) if self.file_data is not None else 0

    def set_playback_index(self, index):
        """Jump to a specific sample index (Seeking)."""
        if self.file_data is not None:
            # Ensure index is within bounds
            self.playback_index = max(0, min(index, len(self.file_data) - 1))