import subprocess
import os
import sys
import requests

class OperatorInterface:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.cwd = os.getcwd()
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Sensitivity Filter
        self.sensitive_patterns = [
            "rm ", "mv ", ">", "chmod", "chown", "sudo", 
            "apt ", "pip install", "python -m pip", "wget", "curl", "kill "
        ]

    def execute_shell(self, command):
        """Executes a shell command with directory awareness."""
        try:
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
            return f"ERROR: {str(e)}"

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

    def manage_power(self, action):
        """Layer 2: Power Control."""
        if action == "sleep": return "SIMULATION: System would enter sleep."
        if action == "reboot": return "SIMULATION: System would reboot."
        return f"ERROR: Unknown power action {action}."

    def proactive_maintenance(self):
        """Layer 14: Survival Instinct (Self-Healing)."""
        import psutil
        disk = psutil.disk_usage(self.cwd)
        if disk.percent > 90:
            return "WARNING: Disk critical (>90%). Suggested Action: Purge logs/temp."
        return "HEALTH: System integrity within safe bounds."

    def list_dir(self, path="."):
        """Layer 1: File System Control."""
        try:
            target = os.path.join(self.cwd, path)
            return "\n".join(os.listdir(target))
        except Exception as e:
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
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            processes.append(proc.info)
        return processes[:20] # Return top 20 for brevity

    def kill_process(self, pid):
        """Layer 1: Process Control."""
        import psutil
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return f"SUCCESS: Terminated PID {pid}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_network_stats(self):
        """Layer 3: Network Observation."""
        import psutil
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv
        }

    def ui_perception(self):
        """Layer 3: UI Perception (Summary)."""
        tree = self.observe_ui_tree()
        active = self.read_active_window()
        return f"ACTIVE_WINDOW: {active}\nTREE_SUMMARY: {str(tree)[:500]}..."

    def capture_screen(self, filename="screenshot.xwd"):
        """Layer 3: Visual Perception (Raw Capture)."""
        try:
            path = os.path.join(self.log_dir, filename)
            subprocess.run(f"xwd -root -out {path}", shell=True, check=True)
            return f"SUCCESS: Screen captured to {path}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def observe_ui_tree(self):
        """Layer 3: Structural Perception (UI Tree)."""
        try:
            result = subprocess.run("xwininfo -tree -root", shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"ERROR: {str(e)}"

    def get_window_metadata(self, window_id):
        """Layer 3: Metadata Perception."""
        try:
            result = subprocess.run(f"xprop -id {window_id}", shell=True, capture_output=True, text=True)
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
            return "UNKNOWN (Likely no active window or non-X11 environment)"

    def is_sensitive(self, command):
        for pattern in self.sensitive_patterns:
            if pattern in command: return True
        return False

    # (Legacy methods retained below for compatibility)
    def read_file(self, path):
        try:
            with open(os.path.join(self.cwd, path), 'r') as f: return f.read()
        except Exception as e: return f"ERROR: {str(e)}"

    def write_file(self, path, content):
        try:
            with open(os.path.join(self.cwd, path), 'w') as f: f.write(content)
            return "SUCCESS"
        except Exception as e: return f"ERROR: {str(e)}"
