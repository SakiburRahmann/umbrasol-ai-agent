import subprocess
import os

class Tools:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Security Blacklist
        self.blacklist = [
            "rm -rf /", "rm -rf ~", "mkfs", "dd if=", 
            "> /dev/sda", "format ", "shutdown", "reboot"
        ]

    def execute_shell(self, command):
        # 1. Check Blacklist
        for forbidden in self.blacklist:
            if forbidden in command:
                return f"ERROR_SECURITY_VIOLATION: Command '{command}' contains blacklisted pattern '{forbidden}'."

        # 2. Execute
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            return {
                "exit_code": result.returncode,
                "output": output
            }
        except subprocess.TimeoutExpired:
            return "ERROR_TIMEOUT: Command took too long to execute."
        except Exception as e:
            return f"ERROR_GENERAL: {str(e)}"

    def write_file(self, path, content):
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"SUCCESS: File written to {path}"
        except Exception as e:
            return f"ERROR_FILE_WRITE: {str(e)}"

    def read_file(self, path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"ERROR_FILE_READ: {str(e)}"
