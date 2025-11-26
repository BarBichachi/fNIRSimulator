# --- LSL Stream Configuration ---
STREAM_NAME = 'fNIRSimulator'
STREAM_TYPE = 'NIRS'
STREAM_ID = 'barbimulator'
SAMPLE_RATE = 50.0  # Data generation and streaming rate (Hz)
NUM_CHANNELS = 32  # 8 optodes × 2 wavelengths × 2 receivers
EXPECTED_PHYSICAL_CHANNELS = NUM_CHANNELS // 2
CHANNEL_NAMES = [f"{prefix}{i}" for prefix in ("L", "R") for i in range(1, 5)]

# --- Wavelength Calibration ---
WL850_GAIN = 1.0
WL760_GAIN = 0.985
WL850_BIAS = 0.005
WL760_BIAS = -0.003

# --- Data Generation Configuration ---
BASE_INTENSITY = 1.2  # Baseline intensity level
NOISE_A = 0.010       # Amplitude of fast (1.2 Hz) noise component
NOISE_B = 0.005       # Amplitude of slow (0.25 Hz) noise component
JITTER_STD = 0.002    # Random Gaussian jitter per sample
HRF_SCALE = 1.0       # Cognitive load response scale
ARTIFACT_SCALE = 0.05 # Artifact amplitude scale

# --- UI Configuration ---
UI_UPDATE_RATE_HZ = 10  # UI refresh rate (Hz)