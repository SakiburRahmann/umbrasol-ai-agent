#!/usr/bin/env python3
"""
Umbrasol Setup Script
Automatically installs platform-specific dependencies
"""
import os
import sys
import subprocess
import platform
import shutil


def run_command(cmd, check=True):
    """Run a shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr


def check_sudo():
    """Check if user has sudo privileges"""
    success, _, _ = run_command("sudo -n true", check=False)
    return success


def install_linux_deps():
    """Install Linux dependencies"""
    print("\n=== Installing Linux Dependencies ===")
    
    deps = [
        "libmpv2",           # For Flet media support
        "libmpv-dev",        # Flet development headers
        "tesseract-ocr",     # OCR support
        "xdotool",           # GUI automation
        "wmctrl",            # Window management
    ]
    
    print("\nRequired packages:")
    for dep in deps:
        print(f"  - {dep}")
    
    if not check_sudo():
        print("\n⚠ This script requires sudo privileges to install system packages.")
        print("Please run: sudo python3 setup_gui.py")
        return False
    
    # Update package list
    print("\nUpdating package list...")
    success, _, err = run_command("sudo apt-get update -qq")
    if not success:
        print(f"Warning: apt-get update failed: {err}")
    
    # Install packages
    print("\nInstalling packages...")
    cmd = f"sudo apt-get install -y {' '.join(deps)}"
    success, out, err = run_command(cmd)
    
    if success:
        print("✓ All Linux dependencies installed successfully")
        return True
    else:
        print(f"✗ Installation failed: {err}")
        return False


def install_python_deps():
    """Install Python dependencies"""
    print("\n=== Installing Python Dependencies ===")
    
    # Determine pip command
    pip_cmd = "pip3" if shutil.which("pip3") else "pip"
    
    # Install from requirements
    print("Installing from requirements.txt...")
    success, out, err = run_command(f"{pip_cmd} install -r requirements.txt")
    
    if not success:
        print(f"Warning: Some packages may have failed: {err}")
    
    # Install Flet
    print("Installing Flet...")
    success, out, err = run_command(f"{pip_cmd} install flet")
    
    if success:
        print("✓ Python dependencies installed successfully")
        return True
    else:
        print(f"✗ Flet installation failed: {err}")
        return False


def setup_windows():
    """Windows-specific setup"""
    print("\n=== Windows Setup ===")
    print("Installing Python dependencies...")
    return install_python_deps()


def setup_android():
    """Android/Termux-specific setup"""
    print("\n=== Android/Termux Setup ===")
    
    # Install Termux packages
    print("Installing Termux packages...")
    packages = ["python", "tesseract", "libmpv"]
    cmd = f"pkg install -y {' '.join(packages)}"
    success, _, _ = run_command(cmd)
    
    if not success:
        print("⚠ Some Termux packages may have failed to install")
    
    return install_python_deps()


def main():
    """Main setup routine"""
    print("=" * 60)
    print("Umbrasol GUI Setup")
    print("=" * 60)
    
    system = platform.system().lower()
    print(f"\nDetected platform: {system}")
    
    if system == "linux":
        # Check if running in Termux
        if os.path.exists("/data/data/com.termux"):
            success = setup_android()
        else:
            success = install_linux_deps() and install_python_deps()
    elif system == "windows":
        success = setup_windows()
    else:
        print(f"⚠ Unsupported platform: {system}")
        success = install_python_deps()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Setup completed successfully!")
        print("\nYou can now run Umbrasol GUI with:")
        print("  python main.py --gui")
    else:
        print("✗ Setup completed with errors")
        print("\nPlease check the error messages above and try again.")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
