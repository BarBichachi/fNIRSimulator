# --- LSL Stream Configuration ---
STREAM_NAME = 'fNIRSimulator'
STREAM_TYPE = 'NIRS'
STREAM_ID = 'barbimulator'
SAMPLE_RATE = 50.0  # Data generation and streaming rate (Hz)
NUM_CHANNELS = 33  # Streamed sample layout: OD32 + ADC1
EXPECTED_PHYSICAL_CHANNELS = 8  # OctaMon: 8 effective channels used by monitor/UI
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

# --- Simulation State Colors ---
STATE_COLORS = {
    "Calm": "#0288d1",         # Blue
    "Cognitive Load": "#ffa000", # Orange
    "Artifact": "#5e35b1"      # Purple
}

# --- OxySoft Placeholder / ADC ---
PLACEHOLDER_HI = 4.81625
PLACEHOLDER_EPS = 0.02
ADC_DEFAULT = 1.48063

# --- OxySoft Direct Channel Mapping (OD) Labels ---
# Order: D1_Rx1_L1..L16, D1_Rx2_L1..L16, ADC1
LSL_CHANNEL_LABELS = (
    [f"D1_Rx1_L{i}" for i in range(1, 17)] +
    [f"D1_Rx2_L{i}" for i in range(1, 17)] +
    ["ADC1"]
)