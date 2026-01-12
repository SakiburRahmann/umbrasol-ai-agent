import sys
import os
import time
import threading
import logging
try:
    from core.tools import OperatorInterface
    from core.brain_v2 import MonolithSoul
    from core.cache import SemanticCache
    from core.habit import HabitManager
    from config import settings
except ImportError:
    from tools import OperatorInterface
    from brain_v2 import MonolithSoul
    from cache import SemanticCache
    from habit import HabitManager
    class settings: MAX_RETRIES = 2; LOG_DIR = "logs"

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
        
        # Identity
        print("--- Umbrasol v7.0: CONTEXT-AWARE CORE ---") # Keep one print for CLI feedback
        self.logger.info(f"System ONLINE | Mode: HYBRID | Voice: {voice_mode}")
        if self.voice_mode:
            self.hands.gui_speak("Systems online. I am listening.")

    def execute(self, user_request):
        start_time = time.time()
        print(f"\n[Request]: {user_request}")
        self.logger.info(f"Requests: {user_request}")

        # LAYER 0: CONTEXT SENSING
        active_window = self.hands.read_active_window()
        context_str = f"[Active Window: {active_window}]"
        self.logger.debug(f"Context: {active_window}")

        # LAYER 1: SEMANTIC CACHE
        cached = self.cache.get(user_request)
        if cached:
            print(f"[CACHE] Hit! Executing known pattern.")
            self.logger.info("Cache Hit")
            result = self._safe_dispatch(cached['tool'], cached['command'])
            self._log_result(result, start_time)
            self.habit.learn(active_window, getattr(result, "tool", "cache"))
            if self.voice_mode: self.speak_result(result)
            return

        # LAYER 2: INSTANT HEURISTICS
        req = user_request.lower().strip()
        instant_map = {
            "battery": ("physical", ""), "power": ("physical", ""),
            "uptime": ("existence", ""), "who am i": ("existence", ""),
            "ram": ("stats", ""), "cpu": ("stats", ""), "stats": ("stats", ""),
            "active window": ("see_active", ""), "list files": ("ls", "."),
            "processes": ("proc_list", ""),
        }
        
        for key, (tool, cmd) in instant_map.items():
            if key in req:
                print(f"[INSTANT] Matched: '{key}' -> {tool}")
                self.logger.info(f"Instant Heuristic: {tool}")
                result = self._safe_dispatch(tool, cmd)
                self._log_result(result, start_time)
                self.habit.learn(active_window, f"{tool}:{cmd}")
                if self.voice_mode: self.speak_result(result)
                return

        # LAYER 3: MINIMAL AI
        print(f"[AI] Novel request. Engaging Brain_v2...")
        self.logger.info("Engaging AI")
        thought = self.soul.execute_task(user_request, context=context_str)
        
        actions = thought.get("actions", [])
        if not actions:
            print("[AI] No actions generated.")
            if self.voice_mode: self.hands.gui_speak("I am unsure how to proceed.")
            return

        success = True
        
        # Execute with Self-Correction
        for action in actions:
            tool = action.get("tool", "stats")
            cmd = action.get("cmd", "")
            
            # Layer 8: Self-Correction Loop
            max_retries = settings.MAX_RETRIES
            action_success = False
            last_result = None
            
            for attempt in range(max_retries + 1):
                result = self._safe_dispatch(tool, cmd)
                res_str = str(result)
                last_result = result
                print(f"[Result]: {res_str[:200]}")
                
                if "ERROR" not in res_str and "BLOCKED" not in res_str:
                    action_success = True
                    break
                
                if attempt < max_retries:
                    print(f"[AUTO-FIX] Action failed. Reflexion initiated...")
                    self.logger.warning(f"Action failed: {tool}({cmd}). Retrying...")
                    error_context = f"Previous action {tool}({cmd}) failed: {result}. Suggest a fix."
                    
                    retry_thought = self.soul.execute_task(user_request, context=context_str + "\n" + error_context)
                    retry_actions = retry_thought.get("actions", [])
                    
                    if retry_actions:
                        new_action = retry_actions[0]
                        tool = new_action.get("tool", tool)
                        cmd = new_action.get("cmd", cmd)
                        print(f"[AUTO-FIX] Retrying with: {tool}({cmd})")
                    else:
                        break
            
            if not action_success:
                success = False
                print(f"[FAILURE] Could not complete task.")
                self.logger.error("Task Failed after retries.")
                self.habit.learn(active_window, f"FAILURE:{user_request}")
                if self.voice_mode: self.hands.gui_speak("I failed to complete the task.")
            else:
                if self.voice_mode: self.speak_result(last_result)
        
        # LAYER 4: LEARNING
        if success and len(actions) == 1:
            action = actions[0]
            self.cache.set(user_request, action['tool'], action['cmd'])
            self.habit.learn(active_window, f"{action['tool']}:{action['cmd']}")
            print("[LEARNING] Pattern cached & habit formed.")

        self.logger.info(f"Execution finished in {time.time() - start_time:.3f}s")
        print(f"[Time]: {time.time() - start_time:.3f}s")

    def speak_result(self, result):
        """Convert result to natural speech."""
        import re
        if isinstance(result, dict):
            # Format dicts like battery/stats
            if "battery" in result:
                text = f"Battery is at {result.get('battery')}."
            elif "identity" in result:
                text = f"I am {result.get('identity')}. System is {result.get('status')}."
            elif "cpu" in result:
                text = f"CPU is at {result['cpu']} percent. RAM is at {result['ram']} percent."
            elif "bytes_sent" in result:
                text = "Network statistics retrieved."
            else:
                text = "Task complete."
        elif isinstance(result, list):
            text = f"I found {len(result)} items."
        else:
            # String result
            res_str = str(result)
            if "active window" in res_str.lower():
                text = res_str.split("|")[1] if "|" in res_str else res_str
            else:
                text = res_str
        
        # FINAL CLEAN: Remove symbols that spd-say might glitch on (---, [[, etc)
        # Keep letters, numbers, and basic punctuation
        clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', ' ', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        if clean_text:
            self.hands.gui_speak(clean_text)

    def _safe_dispatch(self, tool, cmd):
        """Execute ONLY whitelisted safe tools."""
        print(f"[Execute]: {tool}({cmd})")
        self.logger.debug(f"Dispatch: {tool}({cmd})")
        
        try:
            # Dispatch Map
            dispatch = {
                "physical": self.hands.get_physical_state,
                "existence": self.hands.get_existence_stats,
                "stats": self.hands.get_system_stats,
                "see_active": self.hands.read_active_window,
                "see_tree": self.hands.observe_ui_tree,
                "see_raw": self.hands.capture_screen,
                "proc_list": self.hands.get_process_list,
                "net": self.hands.get_network_stats,
                "ls": lambda: self.hands.list_dir(cmd or "."),
                "gui_speak": lambda: threading.Thread(target=self.hands.gui_speak, args=(cmd,)).start()
            }
            
            if tool in dispatch:
                # Handle callable or result
                func = dispatch[tool]
                return func()
            else:
                return f"BLOCKED: Tool '{tool}' not in safety whitelist"
        except Exception as e:
            self.logger.error(f"Dispatch Error: {e}")
            return f"ERROR: {str(e)}"

    def _log_result(self, result, start_time):
        print(f"[Result]: {str(result)[:200]}...")
        print(f"[Time]: {time.time() - start_time:.3f}s")

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
