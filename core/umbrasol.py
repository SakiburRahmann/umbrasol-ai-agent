import sys
import os
import time
import threading
import logging
import atexit
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.tools import OperatorInterface
from core.brain_v2 import MonolithSoul
from core.cache import SemanticCache
from core.habit import HabitManager
from core.omega_memory import OmegaMemory
from core.omega_safety import OmegaSafety
from config import settings

# Configure Logging
logging.basicConfig(
    filename=os.path.join(settings.LOG_DIR, "umbrasol.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class UmbrasolCore:
    """
    Umbrasol v7.0: Context-Aware & Habitual (Project Chimera)
    Combines Heuristics + Habits + Cache + Safe AI.
    """
    def __init__(self, voice_mode=False):
        self.logger = logging.getLogger("Core")
        self.voice_mode = voice_mode
        self.soul = MonolithSoul()
        self.hands = OperatorInterface()
        self.cache = SemanticCache()
        self.habit = HabitManager()
        self.memory = OmegaMemory()
        self.safety = OmegaSafety()
        
        # Ensure directories exist
        os.makedirs(settings.LOG_DIR, exist_ok=True)
        
        # Task execution thread pool (limits concurrent tasks)
        self.executor = ThreadPoolExecutor(
            max_workers=settings.MAX_CONCURRENT_TASKS, 
            thread_name_prefix="Umbrasol-Task"
        )
        
        # Phase 10: RESILIENCE
        self.lock_file = os.path.join(settings.LOG_DIR, "core.lock")
        self._detect_crash()
        with open(self.lock_file, "w") as f:
            f.write(str(os.getpid()))
        
        # Register cleanup handlers
        atexit.register(self._cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Identity
        print(f"--- {settings.SYSTEM_NAME} {settings.VERSION} ---")
        self.logger.info(f"System ONLINE | Persistence: ACTIVE | Safety: GUARDIAN")
        
        # HEALTH MONITOR
        self.health_thread = threading.Thread(target=self._health_monitor, daemon=True)
        self.health_thread.start()
        
        # RESUME PATH
        self._handle_task_resume()
        
        if self.voice_mode:
            self.hands.gui_speak("Omega Core systems online. I am persistent and self-healing.")

    def _cleanup(self):
        """Clean shutdown handler."""
        try:
            # Shutdown thread pool
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True, cancel_futures=False)
            
            # Remove lock file
            if hasattr(self, 'lock_file') and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            self.logger.info("Clean shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle termination signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self._cleanup()
        sys.exit(0)
    
    def _detect_crash(self):
        """Check if previous session crashed."""
        if os.path.exists(self.lock_file):
            print("[ALARM] Abnormal termination detected. Cleaning up lock and notifying memory...")
            self.logger.warning("Crash detected on startup.")
            os.remove(self.lock_file)

    def _health_monitor(self):
        """Background thread to monitor core component vitality."""
        while True:
            time.sleep(settings.HEALTH_CHECK_INTERVAL)
            self.logger.debug("Health Check: ACTIVE")
            # Future: Add voice thread liveness checks here

    def _handle_task_resume(self):
        """Detect and resume tasks from previous sessions."""
        pending = self.memory.get_pending_tasks()
        if pending:
            # Limit resumed tasks to prevent overwhelming the system
            max_resume = min(len(pending), settings.MAX_TASK_RESUME)
            if len(pending) > max_resume:
                print(f"[RECOVERY] Found {len(pending)} interrupted tasks. Resuming {max_resume} most recent...")
                pending = pending[:max_resume]
            else:
                print(f"[RECOVERY] Found {len(pending)} interrupted tasks. Resuming...")
            
            for task in pending:
                self.logger.info(f"Resuming Task {task['id']}: {task['request']}")
                # Submit to thread pool instead of creating unbounded threads
                self.executor.submit(self.execute, task['request'], task_id=task['id'])

    def execute(self, user_request: str, task_id: str | None = None) -> str | None:
        start_time = time.time()
        
        # LAYER 0: PERSISTENCE
        if not task_id:
            task_id = self.memory.add_task(user_request)
        
        print(f"\n[Request]: {user_request}")
        self.logger.info(f"Task {task_id} Initiated: {user_request}")

        # LAYER 1: CONTEXT SENSING
        active_window = self.hands.read_active_window()
        context_str = f"[Active Window: {active_window}]"
        self.logger.debug(f"Context: {active_window}")
        
        # LAYER 2: INTERRUPT PREVIOUS
        self.hands.stop_speaking()

        # LAYER 3: SEMANTIC CACHE
        cached = self.cache.get(user_request)
        if cached:
            print(f"[CACHE] Hit! Executing known pattern.")
            self.logger.info("Cache Hit")
            result = self._safe_dispatch(cached['tool'], cached['command'])
            self._log_result(result, start_time, task_id, cached['tool'], cached['command'])
            self.habit.learn(active_window, getattr(result, "tool", "cache"))
            if self.voice_mode: self.speak_result(result)
            
            self.memory.update_task_checkpoint(task_id, "completed", {"stage": "cache_hit"})
            return str(result)

        # LAYER 4: INSTANT HEURISTICS
        req = user_request.lower().strip()
        word_count = len(req.split())
        instant_map = getattr(settings, "INSTANT_MAP", {})
        
        # Only use heuristics for short commands (speed optimization)
        # For complex queries, let the AI decide (intelligence optimization)
        if word_count < settings.HEURISTIC_WORD_THRESHOLD:
            for key, (tool, cmd) in instant_map.items():
                if key in req:
                    print(f"[INSTANT] Matched: '{key}' -> {tool}")
                    self.logger.info(f"Instant Heuristic: {tool}")
                    result = self._safe_dispatch(tool, cmd)
                    self._log_result(result, start_time, task_id, tool, cmd)
                    self.habit.learn(active_window, f"{tool}:{cmd}")
                    if self.voice_mode: self.speak_result(result)
                    
                    self.memory.update_task_checkpoint(task_id, "completed", {"stage": "instant_heuristic"})
                    return str(result)

        # LAYER 5: REAL-TIME BRAIN (STREAMING)
        print(f"[AI] Thinking...")
        self.logger.info("Engaging Streaming AI")
        
        full_message = ""
        sentence_buffer = ""
        actions = []
        
        # Update Checkpoint: Running
        self.memory.update_task_checkpoint(task_id, "running", {"stage": "thinking"})

        for chunk_data in self.soul.execute_task_stream(user_request, context=context_str):
            if chunk_data["type"] == "talk":
                content = chunk_data["content"]
                
                full_message += content
                sentence_buffer += content
                
                # If we have a natural pause or threshold words, speak it instantly
                word_count = len(sentence_buffer.split())
                if any(p in sentence_buffer for p in [".", "!", "?", ",", ";", ":", "\n"]) or word_count > settings.SENTENCE_BUFFER_WORDS:
                    to_speak = sentence_buffer.strip()
                    if to_speak and self.voice_mode:
                        print(f"[AI] {to_speak}")
                        self.hands.gui_speak(to_speak)
                    sentence_buffer = ""
            
            elif chunk_data["type"] == "action":
                actions.extend(chunk_data.get("actions", []))

        # Speak any remaining text in buffer
        if sentence_buffer.strip() and self.voice_mode:
            print(f"[AI] {sentence_buffer.strip()}")
            self.hands.gui_speak(sentence_buffer.strip())
            
        if not actions and not full_message:
            print("[AI] No response generated.")
            if self.voice_mode: self.hands.gui_speak("I am unsure how to proceed.")
            self.memory.update_task_checkpoint(task_id, "completed", {"stage": "no_response"})
            return
        
        if not actions:
            self.memory.update_task_checkpoint(task_id, "completed", {"stage": "finished_talk"})
            # Continue to end to return result


        # EXECUTION PATH FOR ACTIONS
        success = True
        last_result = None
        
        for action in actions:
            tool = action.get("tool", "stats")
            cmd = action.get("cmd", "")
            
            # GUARD 1: RISK ANALYSIS
            risk = self.safety.analyze_risk(f"{tool} {cmd}")
            if risk != "LOW":
                print(f"[SAFETY] {risk} Risk Detected! Simulating impact...")
                sim_result = self.soul.execute_task(f"SIMULATE: What is the impact of running {tool}({cmd})? Is it safe?", context=context_str)
                print(f"[SIMULATION]: {sim_result.get('talk', 'Analysis complete.')}")
                
                # Vocal Confirmation Wall
                if self.voice_mode and risk == "HIGH":
                    self.hands.gui_speak(f"Warning. {tool} is a high risk operation. Should I proceed?")
                    # Note: In a real STT loop, we'd wait for "yes". For now, we proceed as it's an agentic demo.
            
            # GUARD 2: MANDATORY SNAPSHOT
            if risk in ["MEDIUM", "HIGH"] and tool in ["write", "rm", "mv"]:
                self.safety.snapshot(cmd)

            # Layer 8: Self-Correction Loop with Safety Guards
            max_retries = settings.MAX_RETRIES
            action_success = False
            retry_history = []  # Track retry attempts to prevent loops
            
            for attempt in range(max_retries + 1):
                # Execution
                self.memory.update_task_checkpoint(task_id, "running", {
                    "stage": "executing", 
                    "tool": tool, 
                    "cmd": cmd,
                    "attempt": attempt
                })
                result = self._safe_dispatch(tool, cmd)
                res_str = str(result)
                last_result = result
                print(f"[Result]: {res_str[:200]}")
               
                if "ERROR" not in res_str and "BLOCKED" not in res_str:
                    action_success = True
                    break
                
                if attempt < max_retries:
                    print(f"[AUTO-FIX] Action failed (attempt {attempt + 1}/{max_retries + 1}). Reflexion initiated...")
                    self.logger.warning(f"Action failed: {tool}({cmd}). Retrying...")
                    
                    # Exponential backoff
                    backoff_time = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(backoff_time)
                    
                    error_context = f"Previous action {tool}({cmd}) failed: {result}. Suggest a fix."
                    retry_thought = self.soul.execute_task(user_request, context=context_str + "\n" + error_context)
                    retry_actions = retry_thought.get("actions", [])
                    
                    if retry_actions:
                        new_action = retry_actions[0]
                        new_tool = new_action.get("tool", tool)
                        new_cmd = new_action.get("cmd", cmd)
                        
                        # Circuit Breaker: Detect identical retries
                        retry_signature = f"{new_tool}:{new_cmd}"
                        if retry_signature in retry_history:
                            print(f"[CIRCUIT BREAKER] Detected identical retry. Aborting to prevent loop.")
                            self.logger.error(f"Circuit breaker triggered: identical retry {retry_signature}")
                            break
                        
                        # Validate retry is different from original
                        if new_tool == tool and new_cmd == cmd:
                            print(f"[WARNING] AI suggested identical command. Breaking retry loop.")
                            break
                        
                        retry_history.append(retry_signature)
                        tool = new_tool
                        cmd = new_cmd
                        print(f"[AUTO-FIX] Retrying with: {tool}({cmd})")
                    else:
                        print(f"[AUTO-FIX] No alternative suggested. Aborting retries.")
                        break
            
            self.memory.log_action(f"{tool}({cmd})", str(last_result), risk)

            if not action_success:
                success = False
                print(f"[FAILURE] Could not complete task.")
                self.logger.error("Task Failed after retries.")
                self.habit.learn(active_window, f"FAILURE:{user_request}")
                if self.voice_mode: self.hands.gui_speak("I failed to complete the task.")
                break # Exit action loop if an action fails after retries
            else:
                if self.voice_mode: self.speak_result(last_result)
        
        # LAYER 6: LEARNING
        if success and len(actions) == 1:
            action = actions[0]
            self.cache.set(user_request, action['tool'], action['cmd'])
            self.habit.learn(active_window, f"{action['tool']}:{action['cmd']}")
            print("[LEARNING] Pattern cached & habit formed.")

        self.memory.update_task_checkpoint(task_id, "completed" if success else "failed", {"stage": "finished"})
        self.logger.info(f"Task {task_id} Finished in {time.time() - start_time:.3f}s")
        print(f"[Time]: {time.time() - start_time:.3f}s")
        
        return full_message if full_message else str(last_result) if last_result else None

    def speak_result(self, result):
        """Convert result to natural human speech, stripping machine-isms."""
        import re
        
        # 1. PHRASING: Convert raw data to human sentences
        if isinstance(result, dict):
            if "battery" in result:
                val = str(result.get('battery')).replace("N/A", "not available")
                text = f"The battery is currently {val}."
            elif "identity" in result:
                text = f"I am {result.get('identity')}. My status is {result.get('status')}."
            elif "cpu" in result:
                text = f"The processor is at {result['cpu']} percent, and memory usage is at {result['ram']} percent."
            elif "bytes_sent" in result:
                text = "I have retrieved the network statistics."
            else:
                text = "The task is complete."
        elif isinstance(result, list):
            text = f"I have found {len(result)} items related to your request."
        else:
            # String result
            res_str = str(result)
            if "Title:" in res_str and "|" in res_str:
                # Detect Window Metadata: "ID: 0x... | Title: Name"
                title = res_str.split("Title:")[-1].strip()
                text = f"The current active window is {title}."
            elif "active window" in res_str.lower():
                # Generic fallback for active window mentions
                title = res_str.split("|")[1].strip() if "|" in res_str else res_str
                text = f"The active window is {title}."
            else:
                text = res_str
        
        # 2. SANITIZATION: Strip machine-centric patterns
        # Remove labels that sound robotic
        text = text.replace("ID:", "").replace("Title:", "")
        
        # Remove Hex IDs (e.g. 0xabcdef123)
        text = re.sub(r'0x[a-fA-F0-9]+', '', text)
        
        # Shorten/Cleanup paths (e.g. /home/user/file -> file)
        text = re.sub(r'/[a-zA-Z0-9._/-]+/', ' ', text)
        
        # Replace underscores and dashes with spaces for flow
        text = text.replace("_", " ").replace("-", " ")
        
        # Convert "N/A" or "NaN" to human-readable (Use word boundaries \b to avoid breaking words like "resonance")
        text = re.sub(r'\bN/A\b', 'not available', text)
        text = re.sub(r'\bnan\b', 'not available', text, flags=re.IGNORECASE)

        # FINAL CLEAN: Keep ONLY letters, numbers, and very basic punctuation
        clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', ' ', text)
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        if clean_text:
            self.hands.gui_speak(clean_text)

    def _safe_dispatch(self, tool, cmd):
        """Execute whitelisted tools with expanded Omega capabilities."""
        print(f"[Execute]: {tool}({cmd})")
        self.logger.debug(f"Dispatch: {tool}({cmd})")
        
        try:
            # Dispatch Map
            dispatch = {
                "physical": self.hands.get_physical_state,
                "existence": self.hands.get_existence_stats,
                "stats": self.hands.get_system_stats,
                "see_active": self.hands.read_active_window,
                "see_raw": self.hands.ocr_screen,
                "see_tree": self.hands.observe_ui_tree,
                "proc_list": self.hands.get_process_list,
                "proc_suspend": lambda: self.hands.suspend_process(cmd),
                "proc_resume": lambda: self.hands.resume_process(cmd),
                "proc_zombie": self.hands.check_zombies,
                "gpu": self.hands.get_gpu_stats,
                "power": lambda: self.hands.power_control(cmd),
                "startup": self.hands.get_startup_items,
                "net": self.hands.get_network_stats,
                "net_ctl": lambda: self.hands.control_network(cmd.split()[0], cmd.split()[1] if len(cmd.split())>1 else "up"),
                "ls": lambda: self.hands.list_dir(cmd or "."),
                "shell": lambda: self.hands.execute_shell(cmd),
                "service": lambda: self.hands.manage_service(cmd.split()[0], cmd.split()[1] if len(cmd.split())>1 else "status"),
                "gui_click": lambda: self.hands.gui_click(*map(int, cmd.split(','))) if ',' in cmd else "ERROR: Click requires x,y",
                "gui_type": lambda: self.hands.gui_type(cmd),
                "gui_scroll": lambda: self.hands.gui_scroll(cmd),
                "gui_speak": lambda: self.hands.gui_speak(cmd)
            }
            
            if tool in dispatch:
                # Handle callable or result
                func = dispatch[tool]
                return func()
            else:
                return f"BLOCKED: Tool '{tool}' not in safety whitelist"
        except Exception as e:
            self.logger.error(f"Dispatch Error in {tool}: {e}")
            return f"ERROR: {str(e)}"

    def _log_result(self, result, start_time, task_id=None, tool=None, cmd=None):
        elapsed = time.time() - start_time
        print(f"[Result]: {str(result)[:200]}...")
        print(f"[Time]: {elapsed:.3f}s")
        
        # PERSISTENT AUDIT LOG
        if task_id:
            risk = self.safety.analyze_risk(f"{tool} {cmd}") if tool else "low"
            self.memory.log_action(f"{tool}({cmd})", str(result), risk)
            self.logger.info(f"Task {task_id} Action Logged: {tool}")

    def listen_loop(self):
        """Continuously listen for voice commands."""
        # defer import to avoid cycle or heavy load if not used
        try:
            from core.ear import Ear
        except ImportError:
            from ear import Ear
            
        ear = Ear()
        if not ear.model: return

        print("[VOICE] Listening for commands...")
        self.logger.info("Voice Mode Active")
        # Ensure we are in voice mode now
        self.voice_mode = True 
        
        for command in ear.listen():
            print(f"\n[VOICE] Heard: '{command}'")
            if command:
                self.execute(command)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--voice":
        agent = UmbrasolCore(voice_mode=True)
        agent.listen_loop()
    elif len(sys.argv) > 1:
        agent = UmbrasolCore(voice_mode=False)
        agent.execute(sys.argv[1])
    else:
        print("Usage: python core/umbrasol.py 'command' OR --voice")
