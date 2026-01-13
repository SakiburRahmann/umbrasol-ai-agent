import os

# System Identity
SYSTEM_NAME = "Umbrasol"
VERSION = "v11.0 (Universal Soul)"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
MODELS_DIR = os.path.join(BASE_DIR, "models")
HABIT_MEMORY_PATH = os.path.join(BASE_DIR, "config", "habit_memory.json")

# AI Settings
DEFAULT_MODEL = "qwen2.5:3b"
OLLAMA_BASE_URL = "http://localhost:11434"

# Voice Settings (Dynamic Selection)
PIPER_MODEL_DIR = os.path.join(MODELS_DIR, "voice")
def get_best_voice():
    # Priority: Bryce (Divine) > Ryan (Standard) > Lessac (Light)
    voices = ["en_US-bryce-medium", "en_US-ryan-medium", "en_US-lessac-low"]
    for v in voices:
        if os.path.exists(os.path.join(PIPER_MODEL_DIR, f"{v}.onnx")):
            return v
    return "en_US-ryan-medium" # Default

PIPER_VOICE = get_best_voice()
PIPER_MODEL_PATH = os.path.join(PIPER_MODEL_DIR, f"{PIPER_VOICE}.onnx")

# Execution Settings
MAX_RETRIES = 2
EXECUTION_TIMEOUT = 60

# Safety
SENSITIVE_PATTERNS = [
    "rm ", "mv ", ">", "chmod", "chown", "sudo", 
    "apt ", "pip install", "python -m pip", "wget", "curl", "kill "
]

SAFE_TOOLS = {
    "physical", "existence", "stats", "see_active", "see_tree", 
    "see_raw", "proc_list", "net", "gui_speak", "ls"
}
