import subprocess
import os

class Tools:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.cwd = os.getcwd()
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Security Blacklist
        self.blacklist = [
            "rm -rf /", "rm -rf ~", "mkfs", "dd if=", 
            "> /dev/sda", "format ", "shutdown", "reboot",
            ":(){ :|:& };:", "alias ", "unalias "
        ]

    def execute_shell(self, command):
        """Executes a shell command and returns the output."""
        # 1. Check Blacklist
        for forbidden in self.blacklist:
            if forbidden in command:
                return f"ERROR_SECURITY_VIOLATION: Command '{command}' contains blacklisted pattern '{forbidden}'."

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
