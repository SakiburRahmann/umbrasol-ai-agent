import psutil
import platform
import subprocess

class HardwareProfiler:
    """Hardware profiler for Project Umbrasol to detect system specs and assign an intelligence tier."""
    def __init__(self):
        self.total_ram_gb = psutil.virtual_memory().total / (1024**3)
        self.os_type = platform.system()
        self.has_gpu = self._check_gpu()

    def _check_gpu(self):
        try:
            # Simple check for NVIDIA GPU via nvidia-smi
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def get_tier(self):
        """
        Returns the tier name and the models associated with it.
        """
        # Tier 1: Leviathan (32GB+ RAM or GPU with high VRAM)
        if self.total_ram_gb >= 30 or (self.has_gpu and self.total_ram_gb >= 16):
            return {
                "name": "Leviathan",
                "doer": "glm4.7-thinking",  # Future-proof naming for Ollama
                "guardian": "llama3.1:8b"
            }
        
        # Tier 2: Centurion (8GB - 30GB RAM)
        elif self.total_ram_gb >= 8:
            return {
                "name": "Centurion",
                "doer": "llama3.1:8b",
                "guardian": "phi3:mini"
            }
        
        # Tier 3: Ghost (Under 8GB RAM)
        else:
            return {
                "name": "Ghost",
                "doer": "qwen2.5:3b", # Reliable fallback for low RAM
                "guardian": "phi3:mini"
            }

if __name__ == "__main__":
    profiler = HardwareProfiler()
    tier = profiler.get_tier()
    print(f"System Detected: {profiler.os_type}")
    print(f"RAM: {profiler.total_ram_gb:.2f} GB")
    print(f"GPU Detected: {profiler.has_gpu}")
    print(f"Assigning Tier: {tier['name']}")
    print(f"Active Doer: {tier['doer']}")
    print(f"Active Guardian: {tier['guardian']}")
