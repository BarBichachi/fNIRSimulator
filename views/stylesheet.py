def get_stylesheet():
    return """
    /* ---------- Global ---------- */
    QWidget#MainBackground {
        background-color: #262b35;
    }

    QMainWindow {
        background-color: #111418;
        color: #e0e0e0;
        font-family: "Segoe UI", "Roboto", sans-serif;
        font-size: 13px;
    }

    QLabel {
        background-color: transparent;
        color: #e0e0e0;
        font-size: 14px;
    }
    
     QLabel#OptodeLabel {
        color: black; 
        background-color: transparent;
        border: none;
        font-weight: bold;
    }

    /* ---------- Group Boxes ---------- */
    QGroupBox {
        font-size: 14px;
        font-weight: 600;
        border: 1px solid #3c4655;
        border-radius: 10px;
        margin-top: 10px;
        padding: 6px 4px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 4px;
        color: #dde2ea;
        font-weight: 600;
        font-size: 14px;
    }

    /* ---------- Buttons ---------- */
    QPushButton {
        background-color: #252a33;
        border-radius: 6px;
        border: 1px solid #303641;
        padding: 8px 16px;
        color: #e0e0e0;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #2c323d;
    }
    QPushButton:pressed {
        background-color: #20242c;
    }

    /* Start/Stop Streaming Button */
    QPushButton#PrimaryButton {
        background-color: #2196f3;
        border-color: #2196f3;
        color: white;
        font-weight: 600;
    }
    QPushButton#PrimaryButton:hover {
        background-color: #42a5f5;
    }
    QPushButton#PrimaryButton:checked {
        background-color: #1976D2; /* Darker blue when "Playing" */
        border: 2px solid #fff;
    }

    /* Playback Control Icons */
    QPushButton#PlaybackIconBtn {
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 4px;
    }
    QPushButton#PlaybackIconBtn:hover {
        background-color: #303846;
        border: 1px solid #3c4655;
    }

    /* ---------- Sliders ---------- */
    QSlider::groove:horizontal {
        border: 1px solid #3c4655;
        height: 6px;
        background: #1f242d;
        margin: 2px 0;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #2196f3;
        border: 1px solid #2196f3;
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }

    /* ---------- Separators ---------- */
    QFrame[frameShape="4"] { /* HLine */
        color: #303846; 
    }
    QFrame[frameShape="5"] { /* VLine */
        color: #303846;
    }
    """