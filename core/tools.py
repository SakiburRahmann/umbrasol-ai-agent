import subprocess
import os
import sys
import requests

class Tools:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.cwd = os.getcwd()
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Sensitivity Filter (Commands that trigger the Guardian)
        self.sensitive_patterns = [
            "rm ", "mv ", ">", "chmod", "chown", "sudo", 
            "apt ", "pip install", "python -m pip", "wget", "curl"
        ]

    def execute_shell(self, command):
        """Executes a shell command and returns the output."""
        # 1. Check Blacklist (Hard Veto)
        for forbidden in self.sensitive_patterns:
            if forbidden in command:
                # We still want a hard blacklist for truly dangerous things, 
                # but for now we'll use the sensitive_patterns as the gateway.
                pass 

        # 2. Execute with directory awareness
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=60,
                cwd=self.cwd
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            return {
                "exit_code": result.returncode,
                "output": output
            }
        except subprocess.TimeoutExpired:
            return "ERROR_TIMEOUT: Command took too long to execute (limit 60s)."
        except Exception as e:
            return f"ERROR_GENERAL: {str(e)}"

    def list_dir(self, path="."):
        """Lists files in a directory."""
        try:
            target = os.path.join(self.cwd, path)
            files = os.listdir(target)
            return "\n".join(files)
        except Exception as e:
            return f"ERROR_LS_FAILURE: {str(e)}"

    def change_dir(self, path):
        """Changes the working directory of the agent session."""
        try:
            target = os.path.abspath(os.path.join(self.cwd, path))
            if os.path.isdir(target):
                self.cwd = target
                return f"SUCCESS: Changed directory to {self.cwd}"
            else:
                return f"ERROR_NOT_A_DIRECTORY: {path}"
        except Exception as e:
            return f"ERROR_CD_FAILURE: {str(e)}"

    def write_file(self, path, content):
        """Writes content to a file."""
        try:
            target = os.path.join(self.cwd, path)
            with open(target, 'w') as f:
                f.write(content)
            return f"SUCCESS: File written to {target}"
        except Exception as e:
            return f"ERROR_FILE_WRITE: {str(e)}"

    def read_file(self, path):
        """Reads content from a file."""
        try:
            target = os.path.join(self.cwd, path)
            with open(target, 'r') as f:
                return f.read()
        except Exception as e:
            return f"ERROR_FILE_READ: {str(e)}"

    def execute_python(self, code):
        """The Drill: Executes Python code in a separate process."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.cwd
            )
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return f"ERROR_PYTHON_EXEC: {str(e)}"

    def scrape_web(self, url):
        """The Hook: Fetches text content from a URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Basic cleaning: remove tags (crude but effective for local LLM)
                import re
                clean = re.compile('<.*?>')
                text = re.sub(clean, '', response.text)
                return text[:5000] # Cap to 5k chars for context
            return f"ERROR_HTTP: {response.status_code}"
        except Exception as e:
            return f"ERROR_SCRAPE: {str(e)}"

    def edit_line(self, path, line_number, new_content):
        """The Knife: Edits a specific line in a file."""
        try:
            target = os.path.join(self.cwd, path)
            with open(target, 'r') as f:
                lines = f.readlines()
            
            if 1 <= line_number <= len(lines):
                lines[line_number - 1] = new_content + "\n"
                with open(target, 'w') as f:
                    f.writelines(lines)
                return f"SUCCESS: Line {line_number} updated in {path}"
            return f"ERROR: Line {line_number} out of range (Total lines: {len(lines)})"
        except Exception as e:
            return f"ERROR_LINE_EDIT: {str(e)}"

    def is_sensitive(self, command):
        """Checks if a command requires Guardian validation."""
        for pattern in self.sensitive_patterns:
            if pattern in command:
                return True
        return False

    def get_system_stats(self):
        """The Fork: Returns basic system resource usage."""
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage(self.cwd).percent
        }
