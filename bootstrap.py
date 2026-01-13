import os
import sys
import shutil
import subprocess

# Auto-install psutil for sensing
try:
    import psutil
except ImportError:
    print("Bootstrap: psutil missing. Installing core sensors...")
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil", "--break-system-packages"])
    import psutil

try:
    from config import settings
except ImportError:
    class settings:
        SYSTEM_NAME = "Umbrasol"
        VERSION = "v11.0 (Universal Soul)"

def get_device_info():
    info = {
        "os": sys.platform,
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "cpu_cores": psutil.cpu_count(logical=False),
        "is_android": os.path.exists("/system/build.prop") or shutil.which("termux-info") is not None
    }
    return info

def select_edition(info):
    if info["is_android"] or info["ram_gb"] <= 4:
        return "Light Edition (Optimized for Android/Mobile)", "requirements-android.txt", "small"
    elif info["ram_gb"] > 12:
        return "Divine Edition (Workstation Ready)", "requirements-linux.txt" if info["os"] == "linux" else "requirements-win.txt", "large"
    else:
        return "Standard Edition (Balanced)", "requirements-linux.txt" if info["os"] == "linux" else "requirements-win.txt", "medium"

def main():
    print("--- 🌌 UMBRASOL: DIVINE BOOTSTRAPPER 🌌 ---")
    print("Detecting system specs...")
    info = get_device_info()
    os_name = "Android (Termux)" if info["is_android"] else info["os"]
    print(f"OS: {os_name} | RAM: {info['ram_gb']}GB | Cores: {info['cpu_cores']}")

    edition, req_file, model_scale = select_edition(info)
    print(f"\n[TARGET] {edition}")
    print(f"Dependencies: {req_file}")
    print(f"Model Grade: {model_scale}")

    # 1. Install Dependencies
    print(f"\nInstalling {edition} dependencies...")
    try:
        if os.path.exists(req_file):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
        else:
            print(f"Warning: {req_file} not found. Installing base requirements...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-base.txt"], check=True)
    except Exception as e:
        print(f"Warning: Dependency installation encountered an issue: {e}")

    # 3. Update Settings
    print(f"\nConfiguring {settings.SYSTEM_NAME} identity...")
    try:
        settings_path = os.path.join("config", "settings.py")
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                content = f.read()
            # Update version to reflect graduation if needed
            content = content.replace('VERSION = "v7.0 (Chimera)"', f'VERSION = "{settings.VERSION}"')
            with open(settings_path, "w") as f:
                f.write(content)
        print("[SUCCESS] Platform settings synchronized.")
    except Exception as e:
        print(f"Warning: Could not update settings.py: {e}")

    print("\n[GRADUATION COMPLETE] Umbrasol has adapted to your device.")
    print(f"Type 'python3 main.py' to wake the {edition}.")

if __name__ == "__main__":
    main()
