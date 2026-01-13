# 🌌 Umbrasol: The Chimera AI Agent (v11.0)

> **"The Soul in the Machine."**

![Status](https://img.shields.io/badge/Status-Operational-brightgreen)
![Version](https://img.shields.io/badge/Version-v11.0_Universal_Soul-blueviolet)
![Privacy](https://img.shields.io/badge/Privacy-100%25_Local-blue)
![AI Model](https://img.shields.io/badge/Brain-Qwen_2.5_3B-orange)

**Umbrasol** is a fully autonomous, local AI agent designed for Linux integration. Unlike standard chatbots, Umbrasol has **Hands** to execute system commands, **Eyes** to read your screen, and **Ears** to hear you—all processing occurs offline on your machine.

---

## ⚡ Key Capabilities (v11.0 Update)

| Capability | Tech Stack | Description |
| :--- | :--- | :--- |
| **🧠 Intelligence** | **Qwen 2.5 (3B)** | High-complexity reasoning via Ollama. Capable of simultaneous system action + philosophical conversation. |
| **⚡ Reflex** | **Heuristic Layer** | Instant execution (0.1s) for common tasks (`list files`, `stats`, `battery`). |
| **🗣️ Speech** | **Piper TTS** | High-quality, natural-sounding offline neural speech synthesis. |
| **👂 Hearing** | **Vosk** | Fast, accurate offline speech recognition command loop. |
| **👀 Vision** | **OCR/Scrot** | Reads active window titles and screen text to understand context. |
| **🖐️ Hands** | **System API** | Controls volume, power, files, networks, and processes safely. |
| **💾 Memory** | **SQLite** | Remembers user habits and past conversations (Stored locally in `memory/`). |

---

## ⚡ Simultaneous Processing
Umbrasol v11.0 features a **Dynamic Heuristic Bypass**.
- **Short Commands** (e.g., "check battery") are executed instantly.
- **Complex Commands** (e.g., "Check battery and tell me a poem") are routed to the Brain, allowing the agent to perform the system action **AND** engage in natural conversation in a single turn.

---

## 📦 Installation

### 1. Prerequisites
- **Linux** (Ubuntu/Debian recommended)
- **Ollama** installed and running (`systemctl start ollama`)
- **Python 3.10+**

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/SakiburRahmann/umbrasol-ai-agent.git
cd umbrasol-ai-agent

# Create Environment
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Download Offline Models (Voice/Ear) ~100MB
python3 setup.py
```

---

## 🎮 Usage

### ➤ Human-Like Conversation (Voice Mode)
Talk to Umbrasol hands-free. He will listen to your mic and speak back.
```bash
python3 main.py --voice
```

### ➤ Command Line Interface (Text Mode)
Execute single tasks or queries effectively.
```bash
# Simple System Check
python3 main.py "check battery"

# Complex Reasoning + Action
python3 main.py "Check the CPU temperature and tell me a joke about robots."

# Vision
python3 main.py "read the text on my screen"
```

---

## 🏗️ System Architecture (The Chimera Core)

The project is structured around the **Monolith Soul** (`core/umbrasol.py`), which orchestrates all subsystems:

```mermaid
graph TD
    User[User] -->|Voice/Text| Core[Umbrasol Core]
    Core -->|Short Input| Heuristic[Reflex Layer]
    Core -->|Complex Input| Brain[Brain v2 (Qwen)]
    
    Heuristic --> Tools[Universal Hands]
    Brain --> Tools
    
    Tools -->|Action| System[OS / Filesystem]
    Tools -->|Visual| Eye[OCR / Screen]
    
    Core -->|Text Output| Console
    Core -->|Audio Output| Mouth[Piper TTS]
```

### Module Breakdown
- **`core/umbrasol.py`**: The central nervous system. Handles routing and lifecycle.
- **`core/brain_v2.py`**: The bridge to Ollama/Qwen. Handles streaming and context.
- **`core/tools.py`**: The interface to the OS (shell, gui_click, volume, etc.).
- **`core/ear.py`**: Microphone input processing.
- **`core/habit.py`**: Learning mechanism for user preferences.

---

## 🛡️ Safety & Privacy
- **Destructive Command Block**: Commands like `rm -rf`, `mkfs` are strictly blocked by the Safety Layer.
- **Simulation Mode**: High-risk commands trigger a simulation phase where the AI predicts the impact before asking confirmation.
- **Local Data**: No data is sent to the cloud. Your `memory/` database stays on your disk.

---
*Created by Sakibur Rahman.*
