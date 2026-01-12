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
                    cached_tier = json.load(f)
                    # print(f"[Profiler] Using cached tier: {cached_tier['name']}")
                    return cached_tier
            except: pass

        # 2. Perform Hardware Audit
        ram_gb = psutil.virtual_memory().total / (1024**3)
        has_gpu = self._check_gpu()
        
        # Logic for Tier Assignment
        if ram_gb >= 30 or (has_gpu and ram_gb >= 16):
            tier = {"name": "Leviathan", "doer": "glm4.7-thinking", "guardian": "llama3.1:8b"}
        elif ram_gb >= 8:
            tier = {"name": "Centurion", "doer": "llama3.1:8b", "guardian": "phi3:mini"}
        else:
            tier = {"name": "Ghost", "doer": "qwen2.5:3b", "guardian": "smollm:135m"}

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
        except:
            return False

if __name__ == "__main__":
    profiler = HardwareProfiler()
    tier = profiler.get_tier()
    print(f"System Detected: {profiler.os_type}")
    print(f"RAM: {profiler.total_ram_gb:.2f} GB")
    print(f"GPU Detected: {profiler.has_gpu}")
    print(f"Assigning Tier: {tier['name']}")
    print(f"Active Doer: {tier['doer']}")
    print(f"Active Guardian: {tier['guardian']}")
