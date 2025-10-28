import time
import numpy as np
import math

import config


class DataGenerator:
    """Generates a 16-channel raw fNIRS data sample (8 channels x 2 wavelengths)."""
    def __init__(self):
        self.start_time = time.time()
        self.state = "Calm / Baseline"
        self.state_start_time = self.start_time

    def set_state(self, new_state):
        """Updates the current simulation state."""
        if self.state != new_state:
            self.state = new_state
            self.state_start_time = time.time()

    def restart_state_timer(self):
        """Forces the internal timer for the current state to reset."""
        self.state_start_time = time.time()

    def _generate_hrf_shape(self, t):
        """Generates a canonical Hemodynamic Response Function shape."""
        # A standard gamma function for the HRF
        n, lambda_val = 5, 1.5
        hrf = (t**(n-1) * np.exp(-t/lambda_val)) / (lambda_val**n * math.factorial(n-1))
        return hrf * config.HRF_SCALE  # Scaled for realistic raw intensity change

    def generate_sample(self):
        """Generates a single time-point sample for all channels."""
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        state_time = current_time - self.state_start_time

        # 1. Base physiological noise (heartbeat, respiration)
        base_noise = 10 * np.sin(2 * np.pi * 1.2 * elapsed_time) + \
                     5 * np.sin(2 * np.pi * 0.25 * elapsed_time)

        signal_offset = 0.0

        # 2. Add state-specific signals
        if self.state == "Cognitive Load":
            # The HRF is active during the first 20 seconds of every 30-second interval.
            cycle_time = state_time % 30
            if cycle_time < 20:
                signal_offset = self._generate_hrf_shape(cycle_time)

        elif self.state == "Artifact":
            # The artifact is active during the first second of every 4-second interval.
            if state_time % 4 < 1:
                signal_offset = np.random.uniform(-config.ARTIFACT_SCALE, config.ARTIFACT_SCALE)

        # 3. Create the sample for all channels
        sample = []
        base_intensity = config.BASE_INTENSITY # A typical baseline raw light intensity value

        for i in range(8):  # Loop through 8 channels
            # Each channel gets slightly different random noise
            random_noise = np.random.normal(0, 2)

            # Wavelength 1 (e.g. 760nm) is more sensitive to HHb. Its intensity should INCREASE as HHb falls.
            val1 = base_intensity + base_noise + random_noise + (signal_offset * 0.4)

            # Wavelength 2 (e.g. 850nm) is more sensitive to O2Hb. Its intensity should DECREASE as O2Hb rises.
            val2 = base_intensity + base_noise + random_noise - signal_offset

            sample.extend([val1, val2])

        return sample