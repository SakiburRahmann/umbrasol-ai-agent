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
    os.makedirs(settings.LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(settings.LOG_DIR, "umbrasol.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
        """Interrupt current speech safely."""
        try:
            # Clear pending items from queue safely
            while not self.voice_queue.empty():
                try:
                    self.voice_queue.get_nowait()
                    self.voice_queue.task_done()
                except:
                    break
            
            # Terminate current process if running
            if self.current_proc and self.current_proc.poll() is None:
                try:
                    # Terminate child processes first
                    import psutil
                    parent = psutil.Process(self.current_proc.pid)
                    for child in parent.children(recursive=True):
                        child.terminate()
                    parent.terminate()
                    # Wait briefly for graceful termination
                    parent.wait(timeout=1)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    # Force kill if graceful termination failed
                    if self.current_proc.poll() is None:
                        self.current_proc.kill()
                except Exception as e:
                    self.logger.warning(f"Error terminating voice process: {e}")
            
            return "SUCCESS: Vocal interrupted"
        except Exception as e:
            self.logger.error(f"Stop speaking error: {e}")
            return f"ERROR: {e}"

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
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
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
            os.makedirs(os.path.dirname(filename), exist_ok=True)
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
        # Native PowerShell/user32.dll approach
        script = """
        $signature = '[DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow(); [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);'
        $type = Add-Type -MemberDefinition $signature -Name "Win32Utils" -Namespace "Win32" -PassThru -Using System.Text
        $hwnd = $type::GetForegroundWindow()
        $sb = New-Object System.Text.StringBuilder(256)
        $type::GetWindowText($hwnd, $sb, $sb.Capacity) | Out-Null
        $sb.ToString()
        """
        res = self.execute_shell(script)
        return res.get("output", "UNKNOWN").strip() or "Desktop"

    def ocr_screen(self):
        """OCR for Windows. Uses capture_screen + tesseract if available."""
        try:
            if not shutil.which("tesseract"): return "ERROR: tesseract missing on Windows."
            self.capture_screen()
            path = f"logs/ocr_temp.png" # Assuming last screen saved here or we fix capture_screen to return path
            # For now, we mock the path since capture_screen logic is separate
            res = self.execute_shell(f"tesseract logs/win_shot_latest.png stdout")
            return res.get("output", "OCR: No text detected.")
        except Exception as e: return f"ERROR: Windows OCR failed: {e}"

    def get_process_list(self):
        try:
            return [{"pid": p.pid, "name": p.name(), "cpu": p.cpu_percent(), "mem": p.memory_percent()} for p in psutil.process_iter()][:15]
        except:
            res = self.execute_shell("Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet | ConvertTo-Json")
            return res.get("output", "ERROR: Could not fetch process list")

    def suspend_process(self, pid):
        return self.execute_shell(f"(Get-Process -Id {pid}).Suspend()")
    def resume_process(self, pid):
        return self.execute_shell(f"(Get-Process -Id {pid}).Resume()")
    def check_zombies(self): return "Windows does not have traditional POSIX zombies."
    
    def get_gpu_stats(self):
        try:
            res = self.execute_shell("Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Json")
            return res.get("output", "N/A")
        except: return "N/A"

    def power_control(self, action):
        cmds = {"reboot": "Restart-Computer -Force", "shutdown": "Stop-Computer -Force", "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"}
        if action in cmds:
            self.execute_shell(cmds[action])
            return f"SUCCESS: Executive Windows {action} initiated."
        return f"ERROR: Action {action} unsupported on Windows."

    def get_startup_items(self):
        res = self.execute_shell("Get-CimInstance Win32_StartupCommand | Select-Object Name, Command | ConvertTo-Json")
        return res.get("output", "N/A")

    def manage_service(self, name, action="status"):
        cmd = f"Get-Service -Name {name} | Select-Object Status, DisplayName | ConvertTo-Json" if action == "status" else f"{action}-Service -Name {name}"
        res = self.execute_shell(cmd)
        return res.get("output", str(res))

    def control_network(self, interface, state):
        cmd = f"Disable-NetAdapter -Name '{interface}' -Confirm:$false" if state == "down" else f"Enable-NetAdapter -Name '{interface}' -Confirm:$false"
        return self.execute_shell(cmd)

    def observe_ui_tree(self):
        # UI Automation is complex in PowerShell but possible
        script = "Add-Type -AssemblyName UIAutomationClient; [System.Windows.Automation.AutomationElement]::RootElement.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition) | Select-Object Current"
        res = self.execute_shell(script)
        return res.get("output", "ERROR: UI Tree access restricted.")

    def get_network_stats(self): return psutil.net_io_counters()._asdict()
    def list_dir(self, path="."):
        res = self.execute_shell(f"Get-ChildItem -Path '{path}' | Select-Object Name | ConvertTo-Json")
        return res.get("output", str(os.listdir(path)))

    def capture_screen(self):
        try:
            from PIL import ImageGrab
            timestamp = int(time.time())
            filename = f"logs/win_shot_latest.png"
            ImageGrab.grab().save(filename)
            return f"SUCCESS: Windows screenshot saved to {filename}"
        except Exception as e:
            # PowerShell fallback if Pillow is missing
            filename = f"logs/win_shot_latest.png"
            script = f"Add-Type -AssemblyName System.Windows.Forms, System.Drawing; $Screen = [System.Windows.Forms.Screen]::PrimaryScreen; $Bitmap = New-Object System.Drawing.Bitmap $Screen.Bounds.Width, $Screen.Bounds.Height; $Graphics = [System.Drawing.Graphics]::FromImage($Bitmap); $Graphics.CopyFromScreen($Screen.Bounds.X, $Screen.Bounds.Y, 0, 0, $Bitmap.Size); $Bitmap.Save('{filename}'); $Graphics.Dispose(); $Bitmap.Dispose()"
            self.execute_shell(script)
            return f"SUCCESS: Native Windows capture saved to {filename}"

    def gui_click(self, x, y):
        script = f"""
        $signature = '[DllImport("user32.dll")] public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo); [DllImport("user32.dll")] public static extern void SetCursorPos(int x, int y);'
        $type = Add-Type -MemberDefinition $signature -Name "MouseUtils" -Namespace "Win32" -PassThru
        $type::SetCursorPos({x}, {y})
        $type::mouse_event(0x0002, 0, 0, 0, 0) # Left Down
        $type::mouse_event(0x0004, 0, 0, 0, 0) # Left Up
        """
        self.execute_shell(script)
        return f"SUCCESS: Clicked ({x},{y})"

    def gui_type(self, text):
        script = f"[System.Windows.Forms.SendKeys]::SendWait('{text}')"
        self.execute_shell(script)
        return "SUCCESS: Typed"

    def gui_scroll(self, direction):
        amount = -120 if direction == "down" else 120
        script = f"""
        $signature = '[DllImport("user32.dll")] public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);'
        Add-Type -MemberDefinition $signature -Name "MouseScroll" -Namespace "Win32"
        [Win32.MouseScroll]::mouse_event(0x0800, 0, 0, {amount}, 0)
        """
        self.execute_shell(script)
        return f"SUCCESS: Scrolled {direction}"

    def gui_speak(self, text):
        # Use SAPI.SpVoice via PowerShell
        cmd = f'$speak = New-Object -ComObject SAPI.SpVoice; $speak.Speak("{text}")'
        subprocess.Popen(["powershell", "-Command", cmd], stderr=subprocess.DEVNULL)
        return "SUCCESS: Windows Vocal initiated"

    def stop_speaking(self):
        # Kill any powershell processes that might be speaking
        subprocess.run(["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*powershell*'} | Stop-Process -Force"], stderr=subprocess.DEVNULL)
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
            # Android termux-api can't easily see windows, but we can see the foreground app pkg if root
            res = self.execute_shell("su -c dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
            if res.get("exit_code") == 0: return res["output"].strip()
            
            res = subprocess.run("termux-telephony-deviceinfo", shell=True, capture_output=True, text=True)
            return f"Android Device | Model: {res.stdout.strip()}"
        except: return "Android Device (Foreground Unknown)"

    def ocr_screen(self):
        """OCR for Android using termux-screenshot + tesseract."""
        try:
            if not shutil.which("tesseract"): return "ERROR: tesseract missing. Run: pkg install tesseract"
            path = "logs/android_ocr.png"
            self.capture_screen() # This saves to logs/android_shot.png
            shutil.copy("logs/android_shot.png", path)
            
            res = subprocess.run(f"tesseract {path} stdout", shell=True, capture_output=True, text=True)
            return res.stdout if res.stdout.strip() else "OCR: No text detected."
        except Exception as e: return f"ERROR: OCR failed: {e}"

    def get_process_list(self):
        try:
            return [{"pid": p.pid, "name": p.name(), "mem": p.memory_percent()} for p in psutil.process_iter()][:10]
        except:
            res = self.execute_shell("ps -e")
            return res.get("output", "ERROR: ps failed")

    def suspend_process(self, pid): return self.execute_shell(f"su -c kill -STOP {pid}")
    def resume_process(self, pid): return self.execute_shell(f"su -c kill -CONT {pid}")
    def check_zombies(self): return "No zombie tracking in Android scoped."
    def get_gpu_stats(self): return "N/A (Mobile GPU restricted)"
    
    def power_control(self, action):
        cmds = {"reboot": "su -c reboot", "shutdown": "su -c reboot -p", "sleep": "input keyevent 26"}
        if action in cmds:
            self.execute_shell(cmds[action])
            return f"SUCCESS: Android {action} initiated."
        return f"ERROR: Action {action} unsupported or requires root."

    def get_startup_items(self): return "Execute: ls ~/.termux/boot"
    def manage_service(self, name, action="status"): return f"Android service {action} for {name} (Requires su am/sv)."
    
    def control_network(self, interface, state):
        if shutil.which("termux-wifi-enable"):
            cmd = f"termux-wifi-enable {'true' if state=='up' else 'false'}"
            subprocess.run(cmd, shell=True)
            return f"SUCCESS: WiFi toggled to {state}"
        return "ERROR: termux-api missing"

    def observe_ui_tree(self):
        # Requires ADB/Root
        res = self.execute_shell("su -c uiautomator dump /sdcard/view.xml && su -c cat /sdcard/view.xml")
        return res.get("output", "ERROR: XML Dump failed.")

    def get_network_stats(self): return psutil.net_io_counters()._asdict()
    def list_dir(self, path="."):
        try: return "\n".join(os.listdir(path))
        except: return "ERROR: Access Denied"

    def capture_screen(self):
        if shutil.which("termux-screenshot"):
            subprocess.run("termux-screenshot logs/android_shot.png", shell=True)
            return "SUCCESS: Android screenshot saved to logs/android_shot.png"
        return "ERROR: termux-screenshot missing"

    def gui_click(self, x, y):
        self.execute_shell(f"su -c input tap {x} {y}")
        return f"SUCCESS: Tapped ({x},{y})"

    def gui_type(self, text):
        safe = text.replace(" ", "%s") # input text uses %s for space
        self.execute_shell(f"su -c input text {safe}")
        return "SUCCESS: Typed"

    def gui_scroll(self, direction):
        swipe = "500 1000 500 500" if direction == "down" else "500 500 500 1000"
        self.execute_shell(f"su -c input swipe {swipe}")
        return f"SUCCESS: Scrolled {direction}"

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
