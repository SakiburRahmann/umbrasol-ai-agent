import os
import sys
import zipfile
import subprocess
import shutil
import argparse

# Check if requests is installed
try:
    import requests
except ImportError:
    print("CRITICAL: 'requests' library not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "--break-system-packages"])
    import requests

MODEL_DIR = "models"
VOSK_DIR = os.path.join(MODEL_DIR, "model")
PIPER_DIR = os.path.join(MODEL_DIR, "voice")

SCALES = {
    "small": {
        "vosk": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "vosk_name": "vosk-model-small-en-us-0.15",
        "piper_voice": "en_US-lessac-low" # Light voice
    },
    "medium": {
        "vosk": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "vosk_name": "vosk-model-small-en-us-0.15",
        "piper_voice": "en_US-ryan-medium"
    },
    "large": {
        "vosk": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip", # Higher fidelity
        "vosk_name": "vosk-model-en-us-0.22",
        "piper_voice": "en_US-bryce-medium"
    }
}

def download_file(url, target_path):
    print(f"[DOWNLOAD] {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        with open(target_path, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(chunk_size=8192):
                f.write(data)
                downloaded += len(data)
                if total_size > 0:
                    done = int(50 * downloaded / total_size)
                    sys.stdout.write(f"\r[PROGRESS] [{'=' * done}{' ' * (50-done)}] {downloaded//1024}KB")
                    sys.stdout.flush()
        print("\n[SUCCESS]")
    except Exception as e:
        print(f"\n[ERROR] {e}")

def setup_vosk(scale_data):
    if os.path.exists(VOSK_DIR):
        print("[SETUP] VOSK Model found.")
        return
    os.makedirs(MODEL_DIR, exist_ok=True)
    zip_path = os.path.join(MODEL_DIR, "model.zip")
    download_file(scale_data["vosk"], zip_path)
    print("[SETUP] Unzipping...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(MODEL_DIR)
    shutil.move(os.path.join(MODEL_DIR, scale_data["vosk_name"]), VOSK_DIR)
    os.remove(zip_path)

def setup_piper(scale_data):
    voice = scale_data["piper_voice"]
    os.makedirs(PIPER_DIR, exist_ok=True)
    parts = voice.split("-")
    url_base = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/{parts[1]}/{parts[2]}/"
    for ext in [".onnx", ".onnx.json"]:
        filename = f"{voice}{ext}"
        target = os.path.join(PIPER_DIR, filename)
        if not os.path.exists(target):
            print(f"[SETUP] Downloading Piper {filename}...")
            download_file(url_base + filename, target)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", choices=["small", "medium", "large"], default="medium")
    args = parser.parse_args()
    
    scale_data = SCALES[args.scale]
    print(f"--- Umbrasol Adaptive Setup: {args.scale.upper()} ---")
    setup_vosk(scale_data)
    setup_piper(scale_data)
    
    # Update settings.py dynamically if possible, or just print
    print(f"[INFO] Recommended Settings: PIPER_VOICE = '{scale_data['piper_voice']}'")

if __name__ == "__main__":
    main()
