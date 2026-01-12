import sys
import time
import threading
try:
    from core.tools import OperatorInterface
    from core.brain_v2 import MonolithSoul
    from core.cache import SemanticCache
    from core.habit import HabitManager
except ImportError:
    from tools import OperatorInterface
    from brain_v2 import MonolithSoul
    from cache import SemanticCache
    from habit import HabitManager
# from internet import Internet # To be integrated in Phase 6.X

class UmbrasolCore:
    """
    Umbrasol v6.2: Context-Aware & Habitual (Project Chimera)
    Combines Heuristics + Habits + Cache + Safe AI.
    """
    def __init__(self):
        self.soul = MonolithSoul()
        self.hands = OperatorInterface()
        self.cache = SemanticCache()
        self.habit = HabitManager()
        print("--- Umbrasol v6.2: CONTEXT-AWARE CORE ---")
        print("System: ONLINE | Mode: HYBRID (Heuristic + Habit + Safe AI)")

    def execute(self, user_request):
        start_time = time.time()
        print(f"\n[Request]: {user_request}")

        # LAYER 0: CONTEXT SENSING (Visual)
        active_window = self.hands.read_active_window()
        context_str = f"[Active Window: {active_window}]"
        print(f"[SENSE] Context: {active_window}")

        # LAYER 0.5: HABIT PREDICTION (Subconscious)
        # "If I'm in VS Code at 9am, run 'git status'"
        # habit_cmd, confidence = self.habit.predict(active_window)
        # if habit_cmd:
        #    print(f"[HABIT] Strong pattern detected ({confidence}x). Suggesting: {habit_cmd}")
        #    # Auto-execute or suggest? For now, we trust heuristics first.

        # LAYER 1: SEMANTIC CACHE (0.000s)
        cached = self.cache.get(user_request)
        if cached:
            print(f"[CACHE] Hit! Executing known pattern.")
            result = self._safe_dispatch(cached['tool'], cached['command'])
            print(f"[Result]: {str(result)[:200]}...")
            print(f"[Time]: {time.time() - start_time:.3f}s")
            self.habit.learn(active_window, getattr(result, "tool", "cache")) # Reinforce habit
            return

        # LAYER 2: INSTANT HEURISTICS (0.001s)
        req = user_request.lower().strip()
        instant_map = {
            "battery": ("physical", ""),
            "power": ("physical", ""),
            "uptime": ("existence", ""),
            "who am i": ("existence", ""),
            "ram": ("stats", ""),
            "cpu": ("stats", ""),
            "memory": ("stats", ""),
            "stats": ("stats", ""),
            "active window": ("see_active", ""),
            "what window": ("see_active", ""),
            "list files": ("ls", "."),
            "ls": ("ls", "."),
            "processes": ("proc_list", ""),
        }
        
        for key, (tool, cmd) in instant_map.items():
            if key in req:
                print(f"[INSTANT] Matched: '{key}' -> {tool}")
                result = self._safe_dispatch(tool, cmd)
                print(f"[Result]: {str(result)[:200]}")
                print(f"[Time]: {time.time() - start_time:.3f}s")
                self.habit.learn(active_window, f"{tool}:{cmd}") # Learn this habit
                return

        # LAYER 3: MINIMAL AI (Safety-First + Context)
        print(f"[AI] Novel request. Engaging Brain_v2 with Context...")
        thought = self.soul.execute_task(user_request, context=context_str)
        
        actions = thought.get("actions", [])
        if not actions:
            print("[AI] No actions generated.")
            return

        success = True
        
        # Execute Actions with Self-Correction (Layer 8)
        for action in actions:
            tool = action.get("tool", "stats")
            cmd = action.get("cmd", "")
            
            # Layer 8: Self-Correction Loop
            max_retries = 2
            action_success = False
            
            for attempt in range(max_retries + 1):
                result = self._safe_dispatch(tool, cmd)
                print(f"[Result]: {str(result)[:200]}")
                
                if "ERROR" not in str(result) and "BLOCKED" not in str(result):
                    action_success = True
                    break
                
                # If we failed, reflect and retry
                if attempt < max_retries:
                    print(f"[AUTO-FIX] Action {tool}({cmd}) failed. Reflexion initiated...")
                    error_context = f"Previous action {tool}({cmd}) failed: {result}. Suggest a fix."
                    
                    # Ask Brain for a new plan given the error
                    # We pass the error context to the brain
                    retry_thought = self.soul.execute_task(user_request, context=context_str + "\n" + error_context)
                    retry_actions = retry_thought.get("actions", [])
                    
                    if retry_actions:
                        # Update current action to the new fix
                        new_action = retry_actions[0]
                        tool = new_action.get("tool", tool)
                        cmd = new_action.get("cmd", cmd)
                        print(f"[AUTO-FIX] Retrying with: {tool}({cmd})")
                    else:
                        print("[AUTO-FIX] Brain could not suggest a fix.")
                        break
            
            if not action_success:
                success = False
                print(f"[FAILURE] Could not complete task after {max_retries+1} attempts.")
                self.habit.learn(active_window, f"FAILURE:{user_request}")
        
        # LAYER 4: LEARNING
        if success and len(actions) == 1:
            action = actions[0]
            self.cache.set(user_request, action['tool'], action['cmd'])
            self.habit.learn(active_window, f"{action['tool']}:{action['cmd']}")
            print("[LEARNING] Pattern cached & habit formed.")

        print(f"[Time]: {time.time() - start_time:.3f}s")

    def _safe_dispatch(self, tool, cmd):
        """Execute ONLY whitelisted safe tools."""
        print(f"[Execute]: {tool}({cmd})")
        
        try:
            # SAFETY: Only execute known-safe tools via explicit dispatch
            # This mirrors the whitelist in brain_v2 but enforces it at execution time
            if tool == "physical": return self.hands.get_physical_state()
            elif tool == "existence": return self.hands.get_existence_stats()
            elif tool == "stats": return self.hands.get_system_stats()
            elif tool == "see_active": return self.hands.read_active_window()
            elif tool == "see_tree": return self.hands.observe_ui_tree()
            elif tool == "see_raw": return self.hands.capture_screen()
            elif tool == "proc_list": return self.hands.get_process_list()
            elif tool == "net": return self.hands.get_network_stats()
            elif tool == "ls": return self.hands.list_dir(cmd or ".")
            elif tool == "gui_speak": 
                threading.Thread(target=self.hands.gui_speak, args=(cmd,)).start()
                return "Speaking..."
            else:
                return f"BLOCKED: Tool '{tool}' not in safety whitelist"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def listen_loop(self):
        """Continuously listen for voice commands."""
        from ear import Ear
        ear = Ear()
        if not ear.model: return

        print("[VOICE] Listening for commands... (Say 'check battery')")
        for command in ear.listen():
            print(f"\n[VOICE] Heard: '{command}'")
            if command:
                self.execute(command)

if __name__ == "__main__":
    agent = UmbrasolCore()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--voice":
        agent.listen_loop()
    elif len(sys.argv) > 1:
        agent.execute(sys.argv[1])
    else:
        print("Usage: python core/umbrasol.py 'command' OR --voice")
