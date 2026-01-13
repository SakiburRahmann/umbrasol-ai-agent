import os
import shutil
import logging
import subprocess
import re

class OmegaSafety:
    def __init__(self, backup_dir=".umbrasol/backups"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)
        self.logger = logging.getLogger("Umbrasol.Safety")

    def analyze_risk(self, command):
        """Assigns a risk level to a command using regex patterns."""
        high_risk = [
            r"\brm\s+-rf",        # rm -rf specifically
            r"\breboot\b",        # reboot
            r"\bshutdown\b",      # shutdown
            r"\bformat\b",        # format
            r"\bmkfs\b",          # make filesystem
            r">\s*/dev/",         # write to device
            r"\bdd\b.*of=",       # dd with output file
        ]
        med_risk = [
            r"\brm\s+",           # any rm command
            r"\bmv\s+",           # any mv command
            r"\bsystemctl\s+stop", # stopping services
            r"\bkill\s+-9",       # force kill
            r"\bapt\s+remove",    # package removal
            r"\bpip\s+uninstall", # pip uninstall
            r"\$\(",              # command substitution
            r"`",                 # backtick substitution
        ]
        
        # Check against patterns
        for pattern in high_risk:
            if re.search(pattern, command, re.IGNORECASE):
                return "HIGH"
        for pattern in med_risk:
            if re.search(pattern, command, re.IGNORECASE):
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
