# Umbrasol: The Soulled AI Agent (v7.0) 🦁

**Umbrasol** is a local, autonomous digital operator designed for zero-latency execution, complete privacy, and self-correction. It sees your screen, hears your voice, and predicts your needs.

![Status](https://img.shields.io/badge/Status-Production_Ready-green)
![Version](https://img.shields.io/badge/Version-v7.0_Chimera-blue)
![Architecture](https://img.shields.io/badge/Architecture-Unified_Core-purple)

## 🚀 Key Capabilities
| Layer | Feature | Description |
| :--- | :--- | :--- |
| **0.001s** | **Instant Heuristics** | Executes standard queries (stats, processes, files) instantly. |
| **Ear** | **Offline Voice** | Hands-free command execution via VOSK (No cloud). |
| **Eye** | **Visual Context** | Reads the active window title to understand *where* you are working. |
| **Brain** | **Safe Reasoner** | uses `Qwen2.5/Llama3` for complex planning, with a strict safety whitelist. |
| **Soul** | **Habit Learning** | Learns your routine (Time + App) to predict commands. |
| **Life** | **Self-Correction** | If a command fails, it reflects and retries automatically. |

## 📦 Installation

**1. Clone the Repository**
```bash
git clone https://github.com/SakiburRahmann/umbrasol-ai-agent.git
cd umbrasol-ai-agent
```

**2. Install Dependencies**
```bash
# Recommended: specific virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Run Setup (Auto-Download Models)**
This script will fetch the required AI models (VOSK, etc.) (~50MB) and configure your environment.
```bash
python3 setup.py
```

## 🎮 Usage

**Command Line Mode (Single Shot)**
```bash
python main.py "check battery"
python main.py "what window is open?"
python main.py "list files in core"
```

**Hands-Free Voice Mode**
```bash
python main.py --voice
```
*System will listen. Say "check battery" or "who am i".*

## 🏗️ Architecture (Project Chimera)
The system is built on the **Unified Core** (`core/umbrasol.py`), a single monolith that orchestrates:
1.  **Senses:** (Ear, Eye, Proprioception)
2.  **Reflex:** (Semantic Cache, Heuristics)
3.  **Reason:** (Brain_v2, Habit Manager)
4.  **Action:** (Universal Hands)

## 🛡️ Safety
*   **Local Only:** No data leaves your machine.
*   **Whitelisted:** Destructive commands (`rm`, `sudo`, `dd`) are strictly blocked.
*   **Transparent:** All actions are logged to the console.

---
*Created by the Umbrasol Team (Antigravity). January 2026.*
