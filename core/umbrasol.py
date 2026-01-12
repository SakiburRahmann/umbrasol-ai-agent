import sys
import time
import threading
from tools import OperatorInterface
from brain_v2 import MonolithSoul
from cache import SemanticCache
# from internet import Internet # To be integrated in Phase 6.X

class UmbrasolCore:
    """
    Umbrasol v6.0: The Unified Core (Project Chimera)
    Combines 0.001s Instant Heuristics with Semantic Caching and Safety-First AI.
    """
    def __init__(self):
        self.soul = MonolithSoul()
        self.hands = OperatorInterface()
        self.cache = SemanticCache()
        print("--- Umbrasol v6.0: UNIFIED CORE ---")
        print("System: ONLINE | Mode: HYBRID (Heuristic + Safe AI)")

    def execute(self, user_request):
        start_time = time.time()
        print(f"\n[Request]: {user_request}")

        # LAYER 0: SEMANTIC CACHE (0.000s)
        # Instant recall of previously successful AI executions
        cached = self.cache.get(user_request)
        if cached:
            print(f"[CACHE] Hit! Executing known pattern.")
            result = self._safe_dispatch(cached['tool'], cached['command'])
            print(f"[Result]: {str(result)[:200]}...")
            print(f"[Time]: {time.time() - start_time:.3f}s")
            return

        # LAYER 1: INSTANT HEURISTICS (0.001s)
        # Hardcoded 95% bypass for common system commands
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
                return

        # LAYER 2: MINIMAL AI (Safety-First)
        # Only for novel requests that need reasoning
        print("[AI] Novel request. Engaging Brain_v2...")
        thought = self.soul.execute_task(user_request)
        
        actions = thought.get("actions", [])
        if not actions:
            print("[AI] No actions generated.")
            return

        # Execute Actions with Self-Correction
        success = True
        for action in actions:
            tool = action.get("tool", "stats")
            cmd = action.get("cmd", "")
            
            # Layer 8: Self-Correction Loop could go here (simplified for v6.0)
            result = self._safe_dispatch(tool, cmd)
            print(f"[Result]: {str(result)[:200]}")
            
            if "ERROR" in str(result):
                success = False
                # Future: Trigger self-correction retry here
        
        # LAYER 7: LEARNING
        # If successful, cache the result for next time
        if success and len(actions) == 1:
            # We currently cache simple 1-step actions
            action = actions[0]
            self.cache.set(user_request, action['tool'], action['cmd'])
            print("[LEARNING] Pattern cached for future instant recall.")

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/umbrasol.py 'your command'")
        sys.exit(1)
    
    agent = UmbrasolCore()
    agent.execute(sys.argv[1])
