import numpy as np
import re


def parse_oxysoft_header(filepath):
    """
    Reads the header of an OxySoft .txt export, extracts metadata,
    and finds the line number where the data starts.
    """
    metadata = {
        'Export Date': 'N/A',
        'Start of Measurement': 'N/A',
        'Sample Rate': 10.0,
        'Duration (s)': 0.0,
        'Optode Template': 'N/A',
        'Optode Distance (mm)': 'N/A',
        'DPF': 'N/A',
        'Device ID': 'N/A',
        '# Receivers': 0,
        '# Light Sources': 0,
    }
    data_start_line = 0

    def after_tab_or_colon(line: str) -> str:
        # Prefer tab-split; fall back to colon-split if no tab
        if '\t' in line:
            return line.split('\t', 1)[1].strip()
        return line.split(':', 1)[1].strip() if ':' in line else line.strip()

    def last_float_in_line(line: str, default=None):
        # Find last float (supports integers and decimal like 10 or 10.00)
        nums = re.findall(r'[-+]?\d+(?:\.\d+)?', line)
        return float(nums[-1]) if nums else default

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, raw in enumerate(f):
                line = raw.rstrip('\n')
                if not line.strip():
                    continue

                lower = line.lower()

                # --- Parse Metadata (always strip) ---
                if lower.startswith("export date:"):
                    metadata['Export Date'] = after_tab_or_colon(line)
                elif lower.startswith("start of measurement:"):
                    metadata['Start of Measurement'] = after_tab_or_colon(line)
                elif "sample rate" in lower:
                    # Handles "Datafile sample rate:" or "sample rate:" variants
                    val = last_float_in_line(line, default=metadata['Sample Rate'])
                    if val is not None:
                        metadata['Sample Rate'] = val
                elif lower.startswith("datafile duration:"):
                    # e.g. "Datafile duration:	502.900	s"
                    val = last_float_in_line(line, default=0.0)
                    if val is not None:
                        metadata['Duration (s)'] = val
                elif lower.startswith("optode-template:"):
                    metadata['Optode Template'] = after_tab_or_colon(line)
                elif lower.startswith("optode distance (mm):"):
                    # Some files have a space after the tab; strip handles it
                    metadata['Optode Distance (mm)'] = after_tab_or_colon(line)
                elif lower.startswith("dpf:"):
                    metadata['DPF'] = after_tab_or_colon(line)
                elif lower.startswith("device id:"):
                    metadata['Device ID'] = after_tab_or_colon(line)
                elif lower.startswith("# receivers:"):
                    part = after_tab_or_colon(line)
                    metadata['# Receivers'] = int(re.findall(r'\d+', part)[0]) if re.findall(r'\d+', part) else 0
                elif lower.startswith("# light sources:"):
                    part = after_tab_or_colon(line)
                    metadata['# Light Sources'] = int(re.findall(r'\d+', part)[0]) if re.findall(r'\d+', part) else 0

                # --- Find Data Start Line ---
                # Detect the header row with numbered columns "1  2  3 ... 35"
                cleaned = line.replace('\t', ' ').strip()
                # Heuristic: starts with '1' and contains ' 2 ' and ' 3 '
                if cleaned.startswith('1') and ' 2 ' in cleaned and ' 3 ' in cleaned:
                    data_start_line = i + 1  # data begins on next line
                    break

    except Exception as e:
        print(f"FileLoader: Error parsing header: {e}")
        return None, 0

    if data_start_line == 0:
        print("FileLoader: Could not find data start line.")
        return None, 0

    return metadata, data_start_line


def load_txt_file(filepath, data_start_line):
    """
    Loads all numerical data from an OxySoft .txt export file,
    starting from the specified line.
    """
    try:
        data = np.loadtxt(filepath, skiprows=data_start_line)

        num_cols = data.shape[1]
        if num_cols < 17:
            print(f"FileLoader: Error - Expected at least 17 columns, found {num_cols}")
            return None, 0

        # 32 channels + 1 sample-index column = 33 columns min
        if num_cols >= 33:
            clean_data = data[:, 1:33]  # columns 1..32
        else:
            clean_data = data[:, 1:17]  # assume 8 channels (16 data cols)

        num_channels = clean_data.shape[1]
        print(f"FileLoader: Successfully loaded data with {num_channels} channels.")
        return clean_data, num_channels

    except Exception as e:
        print(f"FileLoader: Error loading numpy data: {e}")
        return None, 0
