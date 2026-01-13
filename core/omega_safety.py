import os
import shutil
import logging
import subprocess

class OmegaSafety:
    def __init__(self, backup_dir=".umbrasol/backups"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        self.logger = logging.getLogger("Umbrasol.Safety")

    def analyze_risk(self, command):
        """Assigns a risk level to a command."""
        high_risk = ["rm -rf", "reboot", "shutdown", "format", "mkfs", "> /dev/"]
        med_risk = ["rm ", "mv ", "systemctl stop", "kill ", "apt remove", "pip uninstall"]
        
        cmd_lower = command.lower()
        if any(trigger in cmd_lower for trigger in high_risk):
            return "HIGH"
        if any(trigger in cmd_lower for trigger in med_risk):
            return "MEDIUM"
        return "LOW"

    def snapshot(self, path):
        """Creates a timestamped backup before modification."""
        if not os.path.exists(path):
            return None
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = os.path.basename(path)
        backup_path = os.path.join(self.backup_dir, f"{name}_{timestamp}")
        
        try:
            if os.path.isdir(path):
                shutil.copytree(path, backup_path)
            else:
                shutil.copy2(path, backup_path)
            self.logger.info(f"SAFETY: Snapshot created for {path} at {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"SAFETY ERROR: Failed to snapshot {path}: {e}")
            return None

    def simulate(self, command, brain):
        """Asks the AI Brain to predict the impact of a command."""
        prompt = f"SIMULATION REQUEST: Analyze the impact of this command: '{command}'. Identify potential risks, side effects, and if it's reversible. Be concise."
        # This will be called by the Core using the Soul's execution method
        return prompt 
