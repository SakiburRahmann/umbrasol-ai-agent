import subprocess
import os
import sys
import shutil
import psutil
import requests
import logging
import threading
import queue
import abc

try:
    from config import settings
except ImportError:
    class settings:
        LOG_DIR = "logs"
        SENSITIVE_PATTERNS = ["rm ", "mv ", "sudo"]
        PIPER_VOICE = "en_US-bryce-medium"
        PIPER_MODEL_DIR = "models/voice"
        PIPER_MODEL_PATH = os.path.join(PIPER_MODEL_DIR, f"{PIPER_VOICE}.onnx")

# Configure Logging
if not os.path.exists(settings.LOG_DIR):
    os.makedirs(settings.LOG_DIR)

logging.basicConfig(
    filename=os.path.join(settings.LOG_DIR, "umbrasol.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BaseHands(abc.ABC):
    """Abstract interface for system-level actions across Linux, Windows, and Android."""
    @abc.abstractmethod
    def execute_shell(self, command): pass
    @abc.abstractmethod
    def get_existence_stats(self): pass
    @abc.abstractmethod
    def get_physical_state(self): pass
    @abc.abstractmethod
    def get_system_stats(self): pass
    @abc.abstractmethod
    def read_active_window(self): pass
    @abc.abstractmethod
    def ocr_screen(self): pass
    @abc.abstractmethod
    def get_process_list(self): pass
    @abc.abstractmethod
    def suspend_process(self, pid): pass
    @abc.abstractmethod
    def resume_process(self, pid): pass
    @abc.abstractmethod
    def check_zombies(self): pass
    @abc.abstractmethod
    def get_gpu_stats(self): pass
    @abc.abstractmethod
    def power_control(self, action): pass
    @abc.abstractmethod
    def get_startup_items(self): pass
    @abc.abstractmethod
    def manage_service(self, name, action="status"): pass
    @abc.abstractmethod
    def control_network(self, interface, state): pass
    @abc.abstractmethod
    def observe_ui_tree(self): pass
    @abc.abstractmethod
    def get_network_stats(self): pass
    @abc.abstractmethod
    def list_dir(self, path="."): pass
    @abc.abstractmethod
    def capture_screen(self): pass
    @abc.abstractmethod
    def gui_click(self, x, y): pass
    @abc.abstractmethod
    def gui_type(self, text): pass
    @abc.abstractmethod
    def gui_scroll(self, direction): pass
    @abc.abstractmethod
    def gui_speak(self, text): pass
    @abc.abstractmethod
    def stop_speaking(self): pass

class LinuxHands(BaseHands):
    def __init__(self):
        self.log_dir = settings.LOG_DIR
        self.cwd = os.getcwd()
        self.logger = logging.getLogger("Umbrasol.LinuxHands")
        
        # PARALLEL VOICE LAYER
        self.voice_queue = queue.Queue()
        self.current_proc = None
        self.voice_thread = threading.Thread(target=self._voice_worker, daemon=True)
        self.voice_thread.start()

    def _voice_worker(self):
        while True:
            try:
                text = self.voice_queue.get()
                if text is None: break
                model_path = settings.PIPER_MODEL_PATH
                if os.path.exists(model_path):
                    play_cmd = "paplay" if shutil.which("paplay") else "aplay"
                    cmd = f"echo '{text}' | piper --model {model_path} --length-scale 0.85 --output-raw | {play_cmd} --raw --rate 22050 --channels 1 --format s16le"
                    self.current_proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.DEVNULL)
                    self.current_proc.wait()
                else:
                    self.current_proc = subprocess.Popen(["spd-say", text])
                    self.current_proc.wait()
                self.voice_queue.task_done()
                self.current_proc = None
            except Exception as e: self.logger.error(f"Voice Error: {e}")

    def stop_speaking(self):
        try:
            with self.voice_queue.mutex: self.voice_queue.queue.clear()
            if self.current_proc and self.current_proc.poll() is None:
                subprocess.run(f"pkill -P {self.current_proc.pid}", shell=True, stderr=subprocess.DEVNULL)
                self.current_proc.terminate()
            subprocess.run("pkill -9 piper", shell=True, stderr=subprocess.DEVNULL)
            subprocess.run("pkill -9 aplay", shell=True, stderr=subprocess.DEVNULL)
            return "SUCCESS: Vocal interrupted"
        except Exception as e: return f"ERROR: {e}"

    def gui_speak(self, text):
        if not text or not text.strip(): return "ERROR: Empty text."
        import re
        clean = re.sub(r'[*_#`]', '', text).strip()
        safe_text = clean.replace("'", "").replace('"', "")
        self.voice_queue.put(safe_text)
        return "SUCCESS: queued"

    def execute_shell(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, cwd=self.cwd)
            return {"exit_code": result.returncode, "output": result.stdout if result.returncode == 0 else result.stderr}
        except Exception as e: return {"exit_code": -1, "output": str(e)}

    def get_existence_stats(self):
        import platform, time
        return {"identity": "Umbrasol Core", "os": platform.system(), "uptime": int(time.time()), "status": "CONSCIOUS"}

    def get_physical_state(self):
        state = {}
        battery = psutil.sensors_battery()
        state["battery"] = f"{battery.percent}%" if battery else "N/A"
        try:
            temps = psutil.sensors_temperatures()
            state["thermal"] = f"{next(iter(temps.values()))[0].current}°C" if temps else "STABLE"
        except: state["thermal"] = "STABLE"
        return state

    def get_system_stats(self):
        return {
            "cpu_total": psutil.cpu_percent(),
            "cpu_cores": psutil.cpu_percent(percpu=True),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage(self.cwd).percent,
            "io": psutil.net_io_counters()._asdict()
        }

    def manage_service(self, name, action="status"):
        """Linux-specific service control (systemd)."""
        cmd = f"systemctl {action} {name}"
        res = self.execute_shell(cmd)
        return res

    def read_active_window(self):
        try:
            res = subprocess.run("xprop -root _NET_ACTIVE_WINDOW", shell=True, capture_output=True, text=True)
            win_id = res.stdout.split()[-1]
            res = subprocess.run(f"xprop -id {win_id} WM_NAME", shell=True, capture_output=True, text=True)
            return res.stdout.split(" = ")[-1].strip('"')
        except: return "UNKNOWN"

    def ocr_screen(self):
        """Optical Character Recognition of the current screen."""
        try:
            from PIL import Image
            import pytesseract
            
            screenshot_path = "logs/ocr_temp.png"
            subprocess.run(f"scrot -o {screenshot_path}", shell=True)
            
            text = pytesseract.image_to_string(Image.open(screenshot_path))
            return text if text.strip() else "OCR: No text detected on screen."
        except Exception as e: return f"ERROR: OCR failed. Ensure tesseract-ocr is installed. {e}"

    def get_process_list(self):
        try:
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                procs.append(proc.info)
            return sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:15]
        except Exception as e: return f"ERROR: {e}"

    def suspend_process(self, pid):
        try:
            p = psutil.Process(int(pid))
            p.suspend()
            return f"SUCCESS: Suspended PID {pid}"
        except Exception as e: return f"ERROR: {e}"

    def resume_process(self, pid):
        try:
            p = psutil.Process(int(pid))
            p.resume()
            return f"SUCCESS: Resumed PID {pid}"
        except Exception as e: return f"ERROR: {e}"

    def check_zombies(self):
        try:
            zombies = [p.info for p in psutil.process_iter(['pid', 'name', 'status']) if p.info['status'] == psutil.STATUS_ZOMBIE]
            return zombies if zombies else "No zombies detected."
        except Exception as e: return f"ERROR: {e}"

    def get_gpu_stats(self):
        """Attempts to get GPU stats via GPUtil (NVIDIA) or fallback."""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                g = gpus[0]
                return f"GPU: {g.name} | Load: {g.load*100:.1f}% | Mem: {g.memoryUsed}MB/{g.memoryTotal}MB"
            return "GPU Monitoring: No active GPUs detected."
        except ImportError:
            try:
                if shutil.which("nvidia-smi"):
                    res = subprocess.run("nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits", shell=True, capture_output=True, text=True)
                    return f"NVIDIA GPU (smi): {res.stdout.strip()}"
                return "GPU Monitoring: GPUtil not installed and nvidia-smi missing."
            except Exception as e: return f"ERROR: {e}"
        except Exception as e: return f"ERROR: {e}"

    def power_control(self, action):
        """reboot, shutdown, sleep."""
        cmds = {"reboot": "reboot", "shutdown": "shutdown now", "sleep": "systemctl suspend"}
        if action in cmds:
            subprocess.run(cmds[action], shell=True)
            return f"SUCCESS: Executive Power action '{action}' initiated."
        return f"ERROR: Unsupported power action '{action}'"

    def get_startup_items(self):
        try:
            res = self.execute_shell("systemctl list-unit-files --type=service --state=enabled")
            return res.get("output", "Could not retrieve startup services.")
        except Exception as e: return f"ERROR: {e}"

    def control_network(self, interface, state):
        """state: up/down"""
        try:
            cmd = f"nmcli device {state} {interface}" if shutil.which("nmcli") else f"ifconfig {interface} {state}"
            return self.execute_shell(cmd)
        except Exception as e: return f"ERROR: {e}"

    def observe_ui_tree(self):
        try:
            res = subprocess.run("xwininfo -tree -root", shell=True, capture_output=True, text=True)
            return res.stdout
        except Exception as e: return f"ERROR: {e}"

    def get_network_stats(self):
        try:
            return psutil.net_io_counters()._asdict()
        except Exception as e: return f"ERROR: {e}"

    def list_dir(self, path="."):
        try:
            target = os.path.abspath(os.path.join(self.cwd, path))
            return "\n".join(os.listdir(target))
        except Exception as e: return f"ERROR: {e}"

    def capture_screen(self):
        try:
            timestamp = int(psutil.time.time())
            filename = f"logs/screenshot_{timestamp}.png"
            subprocess.run(f"import -window root {filename}", shell=True)
            return f"SUCCESS: Screenshot saved to {filename}"
        except Exception as e: return f"ERROR: {e}"

    def gui_click(self, x, y):
        subprocess.run(f"xdotool mousemove {x} {y} click 1", shell=True)
        return f"SUCCESS: Clicked ({x},{y})"

    def gui_type(self, text):
        safe = text.replace("'", "'\"'\"'")
        subprocess.run(f"xdotool type --delay 100 '{safe}'", shell=True)
        return "SUCCESS: Typed"

    def gui_scroll(self, direction):
        btn = "4" if direction == "up" else "5"
        subprocess.run(f"xdotool click --repeat 5 {btn}", shell=True)
        return f"SUCCESS: Scrolled {direction}"

class WindowsHands(BaseHands):
    """Divine Hands for Windows. Uses psutil, pywin32, and native commands."""
    def __init__(self):
        self.cwd = os.getcwd()
        self.logger = logging.getLogger("Umbrasol.WindowsHands")
        # Note: In a real Windows env, we would initialize win32com and pyttsx3 or similar.

    def execute_shell(self, command):
        try:
            # Use powershell for better consistency
            proc = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, timeout=60)
            return {"exit_code": proc.returncode, "output": proc.stdout if proc.returncode == 0 else proc.stderr}
        except Exception as e: return {"exit_code": -1, "output": str(e)}

    def get_existence_stats(self):
        import platform, time
        return {"identity": "Umbrasol Core", "os": "Windows", "uptime": int(time.time()), "status": "CONSCIOUS"}

    def get_physical_state(self):
        battery = psutil.sensors_battery()
        return {"battery": f"{battery.percent}%" if battery else "N/A", "thermal": "N/A (Win sensors restricted)"}

    def get_system_stats(self):
        return {"cpu_total": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "disk": psutil.disk_usage(self.cwd).percent}

    def read_active_window(self):
        # Requires pywin32
        return "UNKNOWN (Requires pywin32)"

    def get_process_list(self):
        try:
            # Use tasklist as fallback if psutil fails
            res = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True, text=True)
            return res.stdout
        except:
            procs = []
            for proc in psutil.process_iter(['pid', 'name']): procs.append(proc.info)
            return procs[:10]

    def suspend_process(self, pid): return f"ERROR: Windows Suspend not native. Try: pssuspend {pid}"
    def resume_process(self, pid): return f"ERROR: Windows Resume not native. Try: psresume {pid}"
    def check_zombies(self): return "Windows uses different process states; no traditional zombies."
    def get_gpu_stats(self):
        try:
            res = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name,AdapterRAM"], capture_output=True, text=True)
            return res.stdout.strip()
        except: return "N/A"
    def power_control(self, action):
        cmds = {"reboot": "shutdown /r /t 0", "shutdown": "shutdown /s /t 0", "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"}
        if action in cmds: os.system(cmds[action]); return f"SUCCESS: Executive Windows {action} initiated."
        return f"ERROR: Action {action} unsupported on Windows."

    def get_startup_items(self):
        try:
            res = subprocess.run(["wmic", "startup", "get", "caption,command"], capture_output=True, text=True)
            return res.stdout
        except: return "Check Registry: HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"

    def manage_service(self, name, action="status"):
        cmd = {"status": "query", "start": "start", "stop": "stop"}.get(action, "query")
        res = subprocess.run(["sc", cmd, name], capture_output=True, text=True)
        return res.stdout
    def control_network(self, interface, state): return "Requires netsh"
    def observe_ui_tree(self): return "Requires accessibility APIs"
    def get_network_stats(self): return psutil.net_io_counters()._asdict()
    def list_dir(self, path="."): return "\n".join(os.listdir(path))
    def capture_screen(self):
        try:
            from PIL import ImageGrab
            timestamp = int(time.time())
            filename = f"logs/screenshot_{timestamp}.png"
            ImageGrab.grab().save(filename)
            return f"SUCCESS: Windows screenshot saved to {filename}"
        except Exception as e: return f"ERROR: Windows capture failed: {e}"

    def gui_speak(self, text):
        # Fallback to powershell SAPI.Say if no other engine
        cmd = f'Add-Type -AssemblyName System.speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}")'
        subprocess.Popen(["powershell", "-Command", cmd], stderr=subprocess.DEVNULL)
        return "SUCCESS: Windows Vocal initiated"

    def stop_speaking(self):
        subprocess.run(["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*powershell*'} | Stop-Process"], stderr=subprocess.DEVNULL)
        return "SUCCESS"

class AndroidHands(BaseHands):
    """Divine Hands for Android (via Termux). Uses termux-api and standard Linux tools."""
    def __init__(self):
        self.cwd = os.getcwd()
        self.logger = logging.getLogger("Umbrasol.AndroidHands")
        self.voice_queue = queue.Queue()
        self.voice_thread = threading.Thread(target=self._voice_worker, daemon=True)
        self.voice_thread.start()

    def _voice_worker(self):
        while True:
            text = self.voice_queue.get()
            if text is None: break
            # Use termux-tts-speak if available, else fallback
            if shutil.which("termux-tts-speak"):
                subprocess.run(f"termux-tts-speak '{text}'", shell=True)
            else:
                self.logger.warning("termux-tts-speak missing. Silent mode.")
            self.voice_queue.task_done()

    def stop_speaking(self):
        # No direct interrupt for termux-tts-speak easily available without pkill
        subprocess.run("pkill -9 termux-tts-speak", shell=True)
        return "SUCCESS"

    def gui_speak(self, text):
        self.voice_queue.put(text)
        return "SUCCESS"

    def execute_shell(self, command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60, cwd=self.cwd)
        return {"exit_code": result.returncode, "output": result.stdout if result.returncode == 0 else result.stderr}

    def get_existence_stats(self):
        import platform, time
        return {"identity": "Umbrasol Core", "os": "Android", "uptime": int(time.time()), "status": "CONSCIOUS"}

    def get_physical_state(self):
        # Use termux-battery-status
        try:
            res = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True)
            import json
            data = json.loads(res.stdout)
            return {"battery": f"{data['percentage']}%", "status": data['status'], "thermal": "N/A"}
        except: return {"battery": "N/A", "thermal": "N/A"}

    def get_system_stats(self):
        return {"cpu_total": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "disk": psutil.disk_usage(self.cwd).percent}

    def read_active_window(self):
        try:
            # Android termux-api can't easily see windows, but we can see the foreground app pkg
            res = subprocess.run("termux-telephony-deviceinfo", shell=True, capture_output=True, text=True)
            return f"Android Device | Model: {res.stdout.strip()}"
        except: return "Android Device (Foreground Unknown)"

    def ocr_screen(self): return "ERROR: Requires tesseract in Termux. Run: pkg install tesseract"
    def get_process_list(self):
        try:
            res = subprocess.run(["ps", "-A"], capture_output=True, text=True)
            return res.stdout[:500] 
        except: return "ERROR: ps failed"

    def suspend_process(self, pid): return "ERROR: Requires Root (kill -STOP)"
    def resume_process(self, pid): return "ERROR: Requires Root (kill -CONT)"
    def check_zombies(self): return "NONE (Termux scoped)"
    def get_gpu_stats(self): return "N/A (Mobile GPU restricted)"
    def power_control(self, action): return "ERROR: Shutdown/Reboot requires Root or termux-api notification trigger"
    def get_startup_items(self): return "Execute: ls ~/.termux/boot"
    def manage_service(self, name, action="status"): return "Execute: sv status " + name
    def control_network(self, interface, state):
        if shutil.which("termux-wifi-enable"):
            cmd = f"termux-wifi-enable {'true' if state=='up' else 'false'}"
            subprocess.run(cmd, shell=True)
            return f"SUCCESS: WiFi toggled to {state}"
        return "ERROR: termux-api missing"
    def observe_ui_tree(self): return "Requires ADB or Accessibility Service"
    def get_network_stats(self): return psutil.net_io_counters()._asdict()
    def list_dir(self, path="."):
        try: return "\n".join(os.listdir(path))
        except: return "ERROR: Access Denied"
    def capture_screen(self):
        if shutil.which("termux-screenshot"):
            subprocess.run("termux-screenshot logs/android_shot.png", shell=True)
            return "SUCCESS: Android screenshot saved to logs/android_shot.png"
        return "ERROR: termux-screenshot missing"
    def gui_click(self, x, y): return f"ERROR: Click requires Root. Cmd: input tap {x} {y}"
    def gui_type(self, text): return f"ERROR: Type requires Root. Cmd: input text {text}"
    def gui_scroll(self, direction): return "ERROR: Scroll requires Root."

def get_operator():
    """Factory to return the correct 'Hands' for the current platform."""
    if sys.platform.startswith("linux"):
        # Check for Android/Termux environment
        if os.path.exists("/system/build.prop") or shutil.which("termux-info"):
            return AndroidHands()
        return LinuxHands()
    elif sys.platform == "win32":
        return WindowsHands()
    return LinuxHands() # Fallback

# For backward compatibility
class OperatorInterface:
    def __new__(cls):
        return get_operator()
