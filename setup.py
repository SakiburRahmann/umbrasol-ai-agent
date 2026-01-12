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

def download_model():
    if os.path.exists(MODEL_PATH):
        print(f"[SETUP] Model found at {MODEL_PATH}. Skipping download.")
        return

    print(f"[SETUP] downloading VOSK model from {MODEL_URL}...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    zip_path = os.path.join(MODEL_DIR, "model.zip")
    
    try:
        response = requests.get(MODEL_URL, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(chunk_size=4096):
                f.write(data)
                downloaded += len(data)
                done = int(50 * downloaded / total_size)
                sys.stdout.write(f"\r[DOWNLOAD] [{'=' * done}{' ' * (50-done)}] {downloaded//1024}KB")
                sys.stdout.flush()
        
        print("\n[SETUP] Unzipping...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(MODEL_DIR)
        
        # Renaissance: Rename extracted folder to 'model'
        extracted_name = "vosk-model-small-en-us-0.15"
        shutil.move(os.path.join(MODEL_DIR, extracted_name), MODEL_PATH)
        
        # Cleanup
        os.remove(zip_path)
        print("[SETUP] Model installed successfully.")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to download model: {e}")
        sys.exit(1)

def main():
    print("--- Umbrasol Setup Wizard (Phase 8.1) ---")
    download_model()
    print("[SETUP] System ready. Run 'python main.py' to start.")

if __name__ == "__main__":
    main()
