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
        """Layer 3: UI Perception (Placeholder for OCR/UI Tree)."""
        return "OBSERVATION: System is currently in CLI mode. GUI perception not active."

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
