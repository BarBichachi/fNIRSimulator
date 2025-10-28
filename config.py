# --- LSL Stream Configuration ---
STREAM_NAME = 'fNIRSimulator'
STREAM_TYPE = 'fNIRS'
STREAM_ID = 'barbimulator'
SAMPLE_RATE = 50  # The rate of data generation and streaming, in Hz.

# --- Data Generation Configuration ---
# The baseline raw light intensity value that the simulation hovers around.
BASE_INTENSITY = 5000

# A scaling factor for the "Cognitive Load" hemodynamic response.
# Higher values make the dip in raw data more pronounced.
HRF_SCALE = 1500

# A scaling factor for the "Artifact" state.
# This determines the max size of the random jump in the data.
ARTIFACT_SCALE = 500

# --- UI Configuration ---
# The rate at which the data display on the UI updates, in Hz.
# This can be slower than the SAMPLE_RATE. 10Hz is smooth for visual feedback.
UI_UPDATE_RATE_HZ = 10