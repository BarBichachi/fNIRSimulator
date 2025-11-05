# logic/file_loader.py

import numpy as np


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
        '# Light Sources': 0
    }
    data_start_line = 0

    try:
        with open(filepath, 'r') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue

                # --- Parse Metadata ---
                if "Export date:" in line:
                    metadata['Export Date'] = line.split('\t', 1)[1]
                elif "Start of measurement:" in line:
                    metadata['Start of Measurement'] = line.split('\t', 1)[1]
                elif "sample rate:" in line:
                    # Find the last valid number in the line
                    parts = line.split()
                    for part in reversed(parts):
                        try:
                            metadata['Sample Rate'] = float(part)
                            break
                        except ValueError:
                            continue
                elif "Datafile duration:" in line:
                    metadata['Duration (s)'] = float(line.split()[-2])
                elif "Optode-template:" in line:
                    metadata['Optode Template'] = line.split('\t', 1)[1]
                elif "Optode distance (mm):" in line:
                    metadata['Optode Distance (mm)'] = line.split('\t')[1]
                elif "DPF:" in line:
                    metadata['DPF'] = line.split('\t')[1]
                elif "Device id:" in line:
                    metadata['Device ID'] = line.split('\t', 1)[1]
                elif "# Receivers:" in line:
                    metadata['# Receivers'] = int(line.split('\t', 1)[1])
                elif "# Light sources:" in line:
                    metadata['# Light Sources'] = int(line.split('\t', 1)[1])

                # --- Find Data Start Line ---
                # A more robust check for the header line (e.g., "1   2   3...")
                cleaned_line = line.replace('\t', ' ').strip()
                if cleaned_line.startswith('1') and ' 2 ' in cleaned_line and ' 3 ' in cleaned_line:
                    data_start_line = i + 1  # The next line is the data
                    break  # Stop parsing, we're done

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
        # --- Load the numerical data using numpy ---
        data = np.loadtxt(filepath, skiprows=data_start_line)

        # --- Clean the data ---
        # The first column is the sample number. We don't need it.
        # We check if the last column is an event column by seeing if it has a low std dev
        if np.std(data[:, -1]) < 0.1 and np.mean(data[:, -1]) < 0.1:  # Event columns are mostly 0
            clean_data = data[:, 1:-1]
        else:
            clean_data = data[:, 1:]  # No event column

        num_channels = clean_data.shape[1]
        print(f"FileLoader: Successfully loaded data with {num_channels} channels.")
        return clean_data, num_channels

    except Exception as e:
        print(f"FileLoader: Error loading numpy data: {e}")
        return None, 0