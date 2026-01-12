import subprocess
import os
import sys
from profiler import HardwareProfiler

class SoulFetcher:
    """Layer 0: Soul Provisioning. Fetches the correct model weights for the device."""
    def __init__(self):
        self.profiler = HardwareProfiler()
        self.tier = self.profiler.get_tier()
        self.soul = self.tier['soul']

    def check_and_fetch(self):
        """Verifies if the model exists locally, if not, pulls it."""
        print(f"[SoulFetcher] System Identified as: {self.tier['name']}")
        print(f"[SoulFetcher] Required Soul: {self.soul}")

        # Check if model exists in Ollama
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if self.soul not in result.stdout:
                print(f"[SoulFetcher] Soul '{self.soul}' not found locally. Initiating Fetch...")
                # In a real app, this would show a progress bar in the UI
                fetch_proc = subprocess.run(["ollama", "pull", self.soul])
                if fetch_proc.returncode == 0:
                    print(f"[SoulFetcher] SUCCESS: Soul '{self.soul}' provisioned.")
                    return True
                else:
                    print(f"[SoulFetcher] FAILURE: Could not fetch soul. Check internet/Ollama.")
                    return False
            else:
                print(f"[SoulFetcher] Soul '{self.soul}' is already present. Optimal State.")
                return True
        except FileNotFoundError:
            print("[SoulFetcher] ERROR: Ollama not found. Please install Ollama to provision souls.")
            return False

if __name__ == "__main__":
    fetcher = SoulFetcher()
    fetcher.check_and_fetch()
