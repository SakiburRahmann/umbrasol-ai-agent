# Project Umbrasol: Master Blueprint
**Status:** Confidential / Internal / Agent-Handoff Ready
**Version:** 1.0.0 (January 2026)

## 0. Executive Summary
Project Umbrasol is an attempt to build a **Universal, 100% Local, Autonomous AI Agent** that performs real-world tasks on behalf of a user. Unlike "chatbots," Umbrasol is a "System Agent." It lives inside the user's operating system (Linux, Windows, Android) and interacts with the hardware and software directly through a "Dual-Soul" architecture. 

It is designed to be **Zero-Cost** (no APIs), **Zero-Latency** (local inference), and **Absolute Privacy** (no data leaves the device).

---

To solve the conflict between "High Autonomy" and "Limited Hardware," Umbrasol uses the **Lite-Memento Architecture**: a speed-optimized version of the original architecture designed for 8GB RAM devices.

### Brain 1: The Doer (Action Intelligence)
- **Role:** The Strategist and Executor.
- **Job:** Takes the user's natural language request ("The Boss"), searches online for the latest info, creates a "Scratchpad" plan, and executes it step-by-step.
- **Target Models (2026):** `GLM-4.7 Thinking` (High reasoning), `Llama 3.1 8B`, `Qwen 2.5 7B`.

### Brain 3: The Universal Hand (Toolkit)
- **Role:** The Executor.
- **Analogy:** "A human hand equipped with a drill, hammer, and surgical blade."
- **Job:** Provides specialized interfaces (Python REPL, Shell, ADB, File API) so the Doer can choose the most efficient "attachment" for the task.

---

## 2. Dynamic Hardware Profiling & Tiered Strategy
Umbrasol includes a **Hardware Profiler** that runs at startup. It detects Total RAM, VRAM (NVIDIA/AMD), and NPU availability to automatically map the system to one of the following intelligence tiers.

### Tier 1: "Leviathan" - High-End PC / Workstation (32GB+ RAM / 16GB+ VRAM)
- **Doer:** `GLM-4.7 Thinking` (355B MoE / 32B Active).
- **Guardian:** `Llama 3.1 8B`.
- **Capability:** Full autonomous system refactoring, advanced research, complex logic.

### Tier 2: "Centurion" - Standard Laptop / Phone (8-16GB RAM)
- **Doer:** `Llama 3.1 8B` (Q4).
- **Guardian:** `Phi-3 Mini` (3.8B).
- **Capability:** Task automation, script writing, organizational work.

### Tier 3: "Ghost" - Budget / Ultra-Battery (Under 8GB RAM)
- **Doer:** `Liquid AI LFM 1.2B` or `Qwen 4B`.
- **Guardian:** `SmolLM 135M`.
- **Capability:** Background monitoring, simple file operations, notification handling.

### Optimization Protocols:
1.  **4-bit Quantization:** All models are compressed using GGUF/EXL2 formats to fit in VRAM/NPU memory.
2.  **NPU Direct-Access:** On mobile, we bypass the CPU/GPU and use the Neural Processing Unit for 10x battery efficiency.
3.  **Zero-Idle Activation:** The LLM is loaded into RAM but "frozen" (no CPU cycles) when not calculating a task.

---

## 3. Operational Modes: Ghost vs. UI
### Ghost Mode (Primary)
- **Method:** Headless execution via Terminal (CLI), ADB Intents, or background API calls.
- **Benefit:** Invisible to the user. Doesn't hijack the screen. Fast.
- **Action Layer:** Scripting (Bash/Python).

### Accessibility Mode (Secondary / Fallback)
- **Method:** Using Android Accessibility APIs or PC Mouse/Keyboard simulation.
- **Benefit:** Can control apps that have no API (e.g., a specific legacy app).
- **Control Layer:** Visual parsing (Screenshot-to-Coordinates).

---

## 4. The Intelligence Layer: Hybrid Memory & Swift Search
Umbrasol prevents "Goldfish Memory" and Hallucinations through a three-tier system:

### A. The "Scratchpad" (Episodic Memory)
- **Analogy:** "A man with short-term memory loss writing on paper."
- **Logic:** For every task, Umbrasol writes its mission plan and results on a temporary "Scratchpad." It re-reads this paper before every single step to avoid losing focus.

### B. The "Life Diary" (Chronic Memory)
- **Analogy:** "Important/Traumatic events remembered for life."
- **Logic:** Significance Check. Only key lessons (e.g., "The user loves dark mode," "This folder is protected") are promoted from the Scratchpad to the permanent Life Diary.

### C. The "Web Look-Aside" (Fact-Check)
- **Logic:** Before starting any task, Umbrasol performs a "Swift Search." It fetches the latest documentation or facts to bridge the "intelligence gap" of small local models.

## 5. Lite Execution Loop (Direct & Safe)
1. **CAPTURE:** Take user request.
2. **TRIAGE:** Check if the task is simple (e.g., "List files"). If yes, skip internet search.
3. **DO:** Execute the step.
4. **SECURE:** If the command matches a sensitive pattern (rm, sudo, etc.), trigger the **Guardian Brain**.
5. **REFLECT:** Record the outcome. Repeat only if the task is incomplete.

---

## 6. Extreme Optimization (Speed & Battery)
To ensure the "Memento Architecture" doesn't become slow or resource-heavy, Umbrasol follows these strict efficiency protocols:

### A. Context Pruning (The "Lean Scratchpad")
- **Logic:** Instead of passing the *entire* history to the LLM every time, Umbrasol uses "Context Distillation." It summarizes past steps into a single "Current State" line before the next thought.
- **Goal:** Keeps token usage low and inference speed high.

### B. Significance-Gated Storage
- **Logic:** The "Life Diary" (Permanent Memory) is pruned. Only key lessons (Significance 8+) are stored in the persistent KV store.
- **Goal:** Rapid lookup and low disk IO.

### C. Swift-Search Caching
- **Logic:** Web results are cached for 1 hour. If a similar task is requested, Umbrasol uses the cache instead of the network.
- **Goal:** Instant response and reduced battery drain.

### D. Zero-Idle Inference
- **Logic:** Models are kept in a "Standby" state using KVCache quantization to ensure the memory footprint is minimal while idle.

---

## 7. Technical Stack
- **Inference Engine:** `Ollama` (Linux/PC/Mac), `llama.cpp` (NPU/Mobile).
- **Application Engine:** `Flutter` (Dart) for Cross-Platform Desktop/Mobile UI.
- **Logic Core:** `Python` (Prototype), `Rust` (Production Shell Interface).
- **Mobile Control:** `Local ADB Bridge` (running on the device itself).

---

## 8. The Universal Hand (Multi-Tool Strategy)
Umbrasol is not just a shell executor. It has a "Universal Hand" with specialized attachments:

1.  **The Drill (Python Runner):** For complex data processing or logic that Shell can't handle.
2.  **The Hook (Web Scraper):** Deep retrieval of info from URLs.
3.  **The Knife (File Surgical API):** Precise editing of code lines without overwriting entire files.
4.  **The Hammer (System Control):** Managing processes, environment variables, and network states.
5.  **The Fork (Multi-Process):** Ability to run tasks in the background while continuing to think.

---

## 9. Implementation Roadmap
### Phase 1: The Desktop Core (Python Prototype)
- Build the "Thinking Loop" between the two brains.
- Implement the Shell Executor with the Blacklist.
- Status: **IN PROGRESS (Jan 2026)**.

### Phase 2: The Cross-Platform Soul (Flutter Integration)
- Port the Python logic to a Flutter App.
- Integrate `llama.cpp` for native NPU performance.
- Build the Android "Ghost Mode" via Intents.

### Phase 3: The Global Agent
- Implement encrypted local logs.
- Multi-Agent coordination (Phone talks to PC to sync tasks).
- Final packaging as .apk, .exe, .dmg.

---

---

## 11. The Switchblade Strategy (Speed vs. Surgery)
To solve the bottleneck of slow local models, Umbrasol uses a "Switchblade" execution model:

1.  **Direct Mode (Fast):** For tasks like `ls`, `mkdir`, `cat`. 
    - No Internet Search.
    - No Guardian Brain.
    - Single-Step JSON output.
    - Result in <10 seconds.

2.  **Surgical Mode (Autonomous):** For tasks like `Refactor this project` or `rm deep-folder`.
    - Triggers the "Memento" recursive loop.
    - Uses Swift-Search and Dual-Soul verification.
    - Result in minutes (High Reliability).

3.  **Heuristic Trigger:** A Python-level filter scans the "Doer" output. If the command contains `rm`, `sudo`, `mv`, or `chmod`, it automatically forces a re-evaluation by the **Guardian Brain**.
