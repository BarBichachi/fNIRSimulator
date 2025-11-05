from PySide6.QtWidgets import QMessageBox


def show_file_info_dialog(parent, filepath, metadata):
    """
    Displays a modal popup with the metadata extracted from the loaded file.
    """
    # Use os.path.basename to get just the filename
    title = f"File Loaded: {filepath.split('/')[-1]}"

    # --- Format the metadata for display ---
    info_text = (
        f"<b>Start Time:</b>\t{metadata['Start of Measurement']}\n"
        f"<b>Duration:</b>\t{metadata['Duration (s)']} s\n"
        f"<b>Sample Rate:</b>\t{metadata['Sample Rate']} Hz\n\n"
        f"<b>Template:</b>\t{metadata['Optode Template']}\n"
        f"<b>Distance:</b>\t{metadata['Optode Distance (mm)']} mm\n"
        f"<b>DPF:</b>\t\t{metadata['DPF']}\n\n"
        f"<b>Device ID:</b>\t{metadata['Device ID']}\n"
        f"<b>Receivers:</b>\t{metadata['# Receivers']}\n"
        f"<b>Light Sources:</b>\t{metadata['# Light Sources']}\n"
    )

    # --- Print to console for history ---
    print("--- File Loaded ---")
    print(info_text.replace("<b>", "").replace("</b>", "").replace("\t", " "))
    print("-------------------")

    # --- Show the popup ---
    QMessageBox.information(parent, title, info_text)