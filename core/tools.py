import subprocess
import os
import sys
import requests
import logging
try:
    from config import settings
except ImportError:
    # Fallback if config package not found (e.g. running directly)
    class settings:
        LOG_DIR = "logs"
        SENSITIVE_PATTERNS = ["rm ", "mv ", "sudo"]

# Configure Logging
logging.basicConfig(
    filename=os.path.join(settings.LOG_DIR, "umbrasol.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class OperatorInterface:
    def __init__(self):
        self.log_dir = settings.LOG_DIR
        self.cwd = os.getcwd()
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        self.logger = logging.getLogger("Hands")

    def execute_shell(self, command):
        """Executes a shell command with directory awareness."""
        try:
            self.logger.info(f"Executing Shell: {command}")
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60,
                cwd=self.cwd
            )
            return {"exit_code": result.returncode, "output": result.stdout if result.returncode == 0 else result.stderr}
        except Exception as e:
            self.logger.error(f"Shell Error: {e}")
            return {"exit_code": -1, "output": f"ERROR: {str(e)}"}

    def get_existence_stats(self):
        """Layer 1: Self-Awareness (Existence)."""
        import time
        import platform
        uptime = 0
        try:
            with open('/proc/uptime', 'r') as f:
                uptime = float(f.readline().split()[0])
        except: 
            uptime = time.time() - os.getloadavg()[0] # Fallback
        
        return {
            "identity": "Umbrasol Core",
            "host": platform.node(),
            "os": platform.system(),
            "uptime_seconds": int(uptime),
            "status": "CONSCIOUS"
        }

    def get_physical_state(self):
        """Layer 2: Physical Dominance (Sensing the Body)."""
        import psutil
        state = {}
        try:
            battery = psutil.sensors_battery()
            state["battery"] = f"{battery.percent}% ({'Charging' if battery.power_plugged else 'Discharging'})" if battery else "N/A"
        except: state["battery"] = "N/A"
        
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                core_temp = next(iter(temps.values()))[0].current
                state["thermal"] = f"{core_temp}°C"
        except: state["thermal"] = "STABLE"
        
        return state

    def list_dir(self, path="."):
        """Layer 1: File System Control."""
        try:
            target = os.path.join(self.cwd, path)
            return "\n".join(os.listdir(target))
        except Exception as e:
            self.logger.error(f"ListDir Error: {e}")
            return f"ERROR: {str(e)}"

    def get_system_stats(self):
        """Layer 1: Resource Monitoring."""
        import psutil
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage(self.cwd).percent
        }

    def get_process_list(self):
        """Layer 1: Process Observation."""
        import psutil
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                processes.append(proc.info)
            return processes[:20]
        except Exception as e:
            self.logger.error(f"ProcList Error: {e}")
            return []

    def get_network_stats(self):
        """Layer 3: Network Observation."""
        import psutil
        try:
            net = psutil.net_io_counters()
            return {
                "bytes_sent": net.bytes_sent,
                "bytes_recv": net.bytes_recv
            }
        except: return {"error": "Network stats unavailable"}

    def capture_screen(self, filename="screenshot.xwd"):
        """Layer 3: Visual Perception (Raw Capture)."""
        try:
            path = os.path.join(self.log_dir, filename)
            subprocess.run(f"xwd -root -out {path}", shell=True, check=True)
            return f"SUCCESS: Screen captured to {path}"
        except Exception as e:
            self.logger.error(f"Screenshot Error: {e}")
            return f"ERROR: {str(e)}"

    def observe_ui_tree(self):
        """Layer 3: Structural Perception (UI Tree)."""
        try:
            result = subprocess.run("xwininfo -tree -root", shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"ERROR: {str(e)}"

    def read_active_window(self):
        """Layer 3: Context Perception."""
        try:
            # Get active window ID from xprop
            res = subprocess.run("xprop -root _NET_ACTIVE_WINDOW", shell=True, capture_output=True, text=True)
            win_id = res.stdout.split()[-1]
            # Get title
            res = subprocess.run(f"xprop -id {win_id} WM_NAME", shell=True, capture_output=True, text=True)
            title = res.stdout.split(" = ")[-1].strip('"')
            return f"ID: {win_id} | Title: {title}"
        except Exception as e:
            self.logger.warning(f"Active Window Read Error: {e}")
            return "UNKNOWN (Likely no active window or non-X11 environment)"

    def gui_click(self, x, y):
        """Layer 9: Universal Hands (Click)."""
        try:
            subprocess.run("which xdotool", shell=True, check=True, capture_output=True)
            subprocess.run(f"xdotool mousemove {x} {y} click 1", shell=True, check=True)
            return f"SUCCESS: Clicked at ({x}, {y})"
        except Exception:
            return "ERROR: Missing 'xdotool'. Please install it to use Universal Hands."

    def gui_type(self, text):
        """Layer 9: Universal Hands (Typing)."""
        try:
            subprocess.run("which xdotool", shell=True, check=True, capture_output=True)
            safe_text = text.replace("'", "'\"'\"'")
            subprocess.run(f"xdotool type --delay 100 '{safe_text}'", shell=True, check=True)
            return f"SUCCESS: Typed text."
        except Exception:
            return "ERROR: Missing 'xdotool'. Please install it to use Universal Hands."

    def gui_scroll(self, direction):
        """Layer 9: Universal Hands (Scrolling)."""
        try:
            btn = "4" if direction == "up" else "5"
            subprocess.run(f"xdotool click --repeat 5 {btn}", shell=True, check=True)
            return f"SUCCESS: Scrolled {direction}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def gui_speak(self, text):
        """Layer 10: Communication (Voice Output)."""
        try:
            subprocess.run(f"spd-say '{text}'", shell=True, check=True)
            return f"SUCCESS: Spoke text."
        except Exception as e:
            return f"ERROR: {str(e)}"
