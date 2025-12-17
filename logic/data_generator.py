import time
import numpy as np
import math
import config


class DataGenerator:
    # Generates data, either simulated or from a file.
    def __init__(self):
        # Initializes the DataGenerator.
        self.start_time = time.time()
        self.state = "Calm"
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
        # Loads file data (rows of 33 values: OD32 + ADC1).
        self.file_data = np.asarray(data, dtype=float)
        self.num_channels = int(num_channels)
        self.playback_index = 0

        # If we loaded 16 channels (8 physical), ensure config matches
        if self.num_channels == 16 and config.NUM_CHANNELS != 16:
            # This is fine, just a log note
            pass

        print(f"DataGenerator: Loaded file data with {self.num_channels} raw values per sample.")

    def unload_file_data(self):
        # Clears the file data and resets to default.
        self.file_data = None
        self.playback_index = 0
        self.num_channels = config.NUM_CHANNELS
        print("DataGenerator: Unloaded file data. Reverting to live simulation (33 values: OD32 + ADC1).")

    def get_playback_status(self):
        """Returns the current playback index and total samples."""
        if self.file_data is not None:
            return self.playback_index, len(self.file_data)
        return 0, 0

    def _generate_live_sample(self):
        # Generate one live sample: 33 values = OD32 (OxySoft order) + ADC1
        t = time.time() - self.start_time
        st = time.time() - self.state_start_time

        # State-dependent offset (HRF or artifacts)
        signal_offset_base = 0.0
        if self.state == "Cognitive Load":
            cycle = st % 30.0
            if cycle < 20.0:
                signal_offset_base = self._generate_hrf_shape(cycle)
        elif self.state == "Artifact":
            if (st % 4.0) < 1.0:
                signal_offset_base = np.random.uniform(-config.ARTIFACT_SCALE, config.ARTIFACT_SCALE)

        def make_rx_active8(rx_bias: float, rx_index: int, ch_offset: int):
            """
            Returns 8 OD values = 4 physical channels × 2 wavelengths (850,760)
            Ordered as: [Ch0_850, Ch0_760, Ch1_850, Ch1_760, Ch2_850, Ch2_760, Ch3_850, Ch3_760]
            """
            out = []
            for j in range(4):
                ch = ch_offset + j  # select which of the 8 personalities to use (0..7)

                freq = self.channel_freq[ch]
                phase = self.channel_phase[ch] + rx_index * 0.3
                gain = self.channel_gain[ch]
                hrf_gain = self.channel_hrf_gain[ch]

                base_noise = (
                        config.NOISE_A * gain * math.sin(2 * math.pi * freq * t + phase) +
                        config.NOISE_B * math.sin(2 * math.pi * 0.25 * t + phase * 0.3)
                )

                local_offset = signal_offset_base * hrf_gain

                if self.state == "Artifact" and signal_offset_base != 0.0:
                    jitter = np.random.uniform(-config.ARTIFACT_SCALE, config.ARTIFACT_SCALE)
                    local_offset += jitter * (0.5 + 0.5 * gain)

                eps = np.random.normal(0.0, config.JITTER_STD)

                # Absolute OD baseline similar scale to real data
                od_baseline = 0.9 + 0.1 * gain

                # Two "wavelength" OD values per physical channel.
                # Keep the same dynamics but slightly different scaling between 850/760.
                od_850 = od_baseline + rx_bias + base_noise + eps + 0.4 * local_offset
                od_760 = od_baseline + rx_bias + base_noise + eps - 1.0 * local_offset

                out.extend([od_850, od_760])

            return out

        ph = config.PLACEHOLDER_HI

        # OctaMon split layout for OxySoft OD32:
        # Rx1 L1..L8 active (4ch×2λ), L9..L16 placeholder
        rx1_active8 = make_rx_active8(rx_bias=0.000, rx_index=0, ch_offset=0)
        rx1_od16 = rx1_active8 + [ph] * 8

        # Rx2 L1..L8 placeholder, L9..L16 active (4ch×2λ)
        rx2_active8 = make_rx_active8(rx_bias=0.005, rx_index=1, ch_offset=4)
        rx2_od16 = [ph] * 8 + rx2_active8

        od32 = rx1_od16 + rx2_od16
        return od32 + [config.ADC_DEFAULT]

    def _generate_playback_sample(self):
        """Return next row from file, converting to raw-like intensity if needed."""
        if self.file_data is None:
            return [0.0] * config.NUM_CHANNELS

        row = self.file_data[self.playback_index]
        self.playback_index = (self.playback_index + 1) % len(self.file_data)

        return row[:config.NUM_CHANNELS]

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