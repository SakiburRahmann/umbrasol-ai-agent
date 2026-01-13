# Umbrasol System Constants
# Centralized configuration constants

import os

# System Identity
SYSTEM_NAME = "Umbrasol"
VERSION = "v12.0 (The Renaissance Soul)"

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
    # Raise error if no voices found (fail fast)
    raise FileNotFoundError(
        f"No Piper voice models found in {PIPER_MODEL_DIR}. "
        "Please run setup.py to download voice models."
    )

try:
    PIPER_VOICE = get_best_voice()
    PIPER_MODEL_PATH = os.path.join(PIPER_MODEL_DIR, f"{PIPER_VOICE}.onnx")
except FileNotFoundError as e:
    # Allow import but warn user
    print(f"WARNING: {e}")
    PIPER_VOICE = None
    PIPER_MODEL_PATH = None

# Execution Settings
MAX_RETRIES = 2
EXECUTION_TIMEOUT = 60
MAX_CONCURRENT_TASKS = 4  # ThreadPoolExecutor worker count
MAX_TASK_RESUME = 10  # Max tasks to resume after crash

# Performance Tuning
HEURISTIC_WORD_THRESHOLD = 5  # Only use heuristics for short commands (< 5 words)
SENTENCE_BUFFER_WORDS = 8  # Speak after accumulating 8 words in streaming
HEALTH_CHECK_INTERVAL = 30  # Seconds between health monitor checks

# Safety Patterns (Regex-based for robust detection)
SENSITIVE_PATTERNS = [
    r"\brm\s+",           # rm with any whitespace
    r"\bmv\s+",           # mv with any whitespace  
    r">+",                # output redirection
    r"\bchmod\b",         # chmod (any usage)
    r"\bchown\b",         # chown (any usage)
    r"\bsudo\b",          # sudo (any usage)
    r"\bapt\s+",          # apt package manager
    r"\bpip\s+install",   # pip install
    r"\bwget\b",          # wget downloads
    r"\bcurl\b.*-o",      # curl with output
    r"\bkill\s+",         # kill process
    r"\$\(",              # command substitution $(...)
    r"`",                 # backtick command substitution
    r"\bdd\b",            # dangerous disk operations
    r"\bmkfs\b",          # filesystem creation
    r">\s*/dev/",         # writing to device files
]

# Heuristic Mapping (0.00ms Instant Commands)
INSTANT_MAP = {
    "battery": ("physical", ""), "power": ("physical", ""),
    "uptime": ("existence", ""), 
    "ram": ("stats", ""), "cpu": ("stats", ""), "stats": ("stats", ""),
    "active window": ("see_active", ""), "list files": ("ls", "."),
    "processes": ("proc_list", ""),
}

# Tool Whitelist
SAFE_TOOLS = {
    "physical", "existence", "stats", "see_active", "see_tree", 
    "see_raw", "proc_list", "net", "gui_speak", "ls",
    "gpu", "power", "startup", "shell", "service", 
    "gui_click", "gui_type", "gui_scroll"
}
