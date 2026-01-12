import os

# System Identity
SYSTEM_NAME = "Umbrasol"
VERSION = "v7.0 (Chimera)"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
MODELS_DIR = os.path.join(BASE_DIR, "models")
HABIT_MEMORY_PATH = os.path.join(BASE_DIR, "config", "habit_memory.json")

# AI Settings
DEFAULT_MODEL = "qwen2.5:3b"
OLLAMA_BASE_URL = "http://localhost:11434"

# Voice Settings (Piper)
PIPER_MODEL_DIR = os.path.join(MODELS_DIR, "voice")
PIPER_VOICE = "en_US-lessac-medium" # Neural voice model
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
