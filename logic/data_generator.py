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
        self.num_channels = 16  # Default to 16-stream (8-channel)

    def set_state(self, new_state):
        """Updates the current simulation state."""
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = time.time()

    def restart_state_timer(self):
        """Forces the internal timer for the current state to reset."""
        self.state_start_time = time.time()

    def load_file_data(self, data, num_channels):
        # Loads data from a file into the generator.
        self.file_data = data
        self.num_channels = num_channels
        self.playback_index = 0

    def unload_file_data(self):
        # Clears the file data and resets to default.
        self.file_data = None
        self.playback_index = 0
        self.num_channels = 16

    def _generate_live_sample(self):
        # Generates a single sample of live, simulated data.
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        state_time = current_time - self.state_start_time

        # --- Base physiological noise ---
        base_noise = 10 * np.sin(2 * np.pi * 1.2 * elapsed_time) + \
                     5 * np.sin(2 * np.pi * 0.25 * elapsed_time)

        signal_offset = 0.0

        # --- Add state-specific signals based on state_time ---
        if self.state == "Cognitive Load":
            # The HRF is active during the first 20 seconds of every 30-second interval.
            cycle_time = state_time % 30
            if cycle_time < 20:
                signal_offset = self._generate_hrf_shape(cycle_time)

        elif self.state == "Artifact":
            # The artifact is active during the first second of every 4-second interval.
            if state_time % 4 < 1:
                signal_offset = np.random.uniform(-config.ARTIFACT_SCALE, config.ARTIFACT_SCALE)

        # --- Create the sample for all 8 channels (16 streams) ---
        sample = []
        base_intensity = config.BASE_INTENSITY
        for i in range(8):
            random_noise = np.random.normal(0, 2)
            # Wavelength 1 (e.g. 760nm)
            val1 = base_intensity + base_noise + random_noise + (signal_offset * 0.4)
            # Wavelength 2 (e.g. 850nm)
            val2 = base_intensity + base_noise + random_noise - signal_offset
            sample.extend([val1, val2])

        return sample

    def _generate_playback_sample(self):
        # Fetches the next sample from the loaded file data.
        if self.file_data is None:
            return [0] * self.num_channels

        # Get the current row of OD data
        od_data = self.file_data[self.playback_index]

        # --- Convert OD data to Simulated Raw Intensity ---
        # This makes it compatible with our fNIRS_Monitor's DataProcessor
        simulated_raw = 5000 - (od_data * 100)

        # Advance the index and loop back to the start if we reach the end
        self.playback_index = (self.playback_index + 1) % len(self.file_data)

        return simulated_raw

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