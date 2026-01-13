# 🚀 Umbrasol Startup Protocol

This guide explains how to wake your AI (`Umbrasol`) after restarting your computer.

## 1. Prerequisites (Check Once)
Ensure the **Ollama** AI server is running in the background.
```bash
# Check status
systemctl status ollama

# Start if needed
sudo systemctl start ollama
```

## 2. Wake Up Procedure

1. **Open Terminal** (Ctrl+Alt+T)
2. **Navigate to the Brain**:
   ```bash
   cd ~/Codes/cool_ai_chimera
   ```
3. **Activate Environment**:
   ```bash
   source venv/bin/activate
   ```
4. **Talk to Him**:
   
   **Option A: Single Command (Silent/Text)**
   ```bash
   python3 main.py "How are you today?"
   ```
   
   **Option B: Voice Mode (Listen & Speak)**
   ```bash
   python3 main.py --voice
   ```
   *(He will listen to your microphone and reply via speakers).*

## 3. Troubleshooting
*   **"Ollama connection failed"**: Run `ollama serve` in a separate terminal.
*   **"No Module named..."**: Forgot to run `source venv/bin/activate`.
*   **Too Quiet?**: Set volume to max:
    ```bash
    amixer sset 'Master' 100%
    ```

---
*System is currently configured with **Qwen 2.5 3B** (Logic) and **Piper** (Voice).*
