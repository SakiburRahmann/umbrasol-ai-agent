import os
import sys
import zipfile
import subprocess
import shutil

# Check if requests is installed, if not, warn
try:
    import requests
except ImportError:
    print("CRITICAL: 'requests' library not found. Please run: pip install -r requirements.txt")
    sys.exit(1)

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "model")

# Piper Settings
PIPER_VOICE = "en_US-lessac-medium"
PIPER_URL_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/"
PIPER_FILES = [f"{PIPER_VOICE}.onnx", f"{PIPER_VOICE}.onnx.json"]
PIPER_DIR = os.path.join(MODEL_DIR, "voice")

def download_file(url, target_path):
    print(f"[DOWNLOAD] {url} -> {target_path}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(target_path, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(chunk_size=4096):
                f.write(data)
                downloaded += len(data)
                if total_size > 0:
                    done = int(50 * downloaded / total_size)
                    sys.stdout.write(f"\r[PROGRESS] [{'=' * done}{' ' * (50-done)}] {downloaded//1024}KB")
                    sys.stdout.flush()
        print("\n[SUCCESS] Download complete.")
    except Exception as e:
        print(f"\n[ERROR] Failed to download {url}: {e}")
        sys.exit(1)

def download_vosk_model():
    if os.path.exists(MODEL_PATH):
        print(f"[SETUP] VOSK Model found. Skipping.")
        return

    print(f"[SETUP] Downloading VOSK model...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    zip_path = os.path.join(MODEL_DIR, "model.zip")
    download_file(MODEL_URL, zip_path)
    
    print("[SETUP] Unzipping...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(MODEL_DIR)
    
    shutil.move(os.path.join(MODEL_DIR, "vosk-model-small-en-us-0.15"), MODEL_PATH)
    os.remove(zip_path)

def download_piper_model():
    os.makedirs(PIPER_DIR, exist_ok=True)
    for filename in PIPER_FILES:
        target = os.path.join(PIPER_DIR, filename)
        if os.path.exists(target):
            print(f"[SETUP] Piper file {filename} found. Skipping.")
            continue
        
        print(f"[SETUP] Downloading Piper neural voice: {filename}...")
        download_file(PIPER_URL_BASE + filename, target)

def main():
    print("--- Umbrasol Setup Wizard (Phase 8.5) ---")
    download_vosk_model()
    download_piper_model()
    print("[SETUP] System ready. Run 'python main.py' to start.")

if __name__ == "__main__":
    main()
