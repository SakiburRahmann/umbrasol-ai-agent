import psutil
import platform
import subprocess
import os
import json

class HardwareProfiler:
    """Hardware profiler that remembers its results in config/system_profile.json."""
    def __init__(self, config_path="config/system_profile.json"):
        self.config_path = config_path
        self.os_type = platform.system()

    def get_tier(self):
        # 1. Check Cache
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Profiler Warning: Could not read cache: {e}")

        # 2. Perform Hardware Audit
        ram_gb = psutil.virtual_memory().total / (1024**3)
        has_gpu = self._check_gpu()
        
        # Mono-Soul Logic: One high-quality model per tier
        if ram_gb >= 30 or (has_gpu and ram_gb >= 16):
            tier = {"name": "Leviathan", "soul": "glm4.7-thinking"}
        elif ram_gb >= 8:
            tier = {"name": "Centurion", "soul": "llama3.1:8b"}
        else:
            tier = {"name": "Ghost", "soul": "qwen2.5:3b"}

        # 3. Save Cache
        try:
            if not os.path.exists("config"): os.makedirs("config")
            with open(self.config_path, 'w') as f:
                json.dump(tier, f)
        except: pass

        return tier

    def _check_gpu(self):
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            return False

if __name__ == "__main__":
    profiler = HardwareProfiler()
    tier = profiler.get_tier()
    print(f"System Detected: {profiler.os_type}")
    print(f"Assigning Tier: {tier['name']}")
    print(f"Active Soul: {tier['soul']}")
