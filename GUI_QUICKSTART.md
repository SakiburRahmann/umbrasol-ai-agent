# Umbrasol GUI - Quick Start Guide

## Installation

### Step 1: Run the automated setup script

The setup script will automatically install all required dependencies for your platform.

**Linux:**
```bash
sudo python3 setup_gui.py
```

**Windows:**
```bash
python setup_gui.py
```

**Android (Termux):**
```bash
python setup_gui.py
```

### Step 2: Launch the GUI

```bash
python main.py --gui
```

## What Gets Installed

### Linux Dependencies
- `libmpv2` - Media playback support for Flet
- `libmpv-dev` - Development headers
- `tesseract-ocr` - OCR capabilities
- `xdotool` - GUI automation
- `wmctrl` - Window management

### Python Dependencies
- `flet` - Modern GUI framework (Flutter in Python)
- All packages from `requirements.txt`

### Windows Dependencies
- Python packages only (no system dependencies required)

### Android Dependencies
- Termux packages: python, tesseract, libmpv
- Python packages from requirements

## Troubleshooting

### "libmpv.so.2: cannot open shared object file"
Run the setup script with sudo:
```bash
sudo python3 setup_gui.py
```

### "Permission denied"
Make the setup script executable:
```bash
chmod +x setup_gui.py
```

### GUI doesn't open
Check if Flet is installed:
```bash
pip list | grep flet
```

If not installed, run:
```bash
pip install flet
```

## Features

- Modern Material Design 3 interface
- Real-time AI conversation
- Cross-platform (Windows, Linux, Android)
- Native keyboard input (no browser issues)
- Direct Python integration with Umbrasol Core
- Background processing for responsive UI

## Usage

1. Type your command or question in the input field
2. Press Enter or click the send button
3. Wait for Umbrasol to process and respond
4. Continue the conversation naturally

The GUI supports all Umbrasol capabilities including:
- System automation
- File operations
- Web searches
- Code execution
- Memory recall
- And more...
