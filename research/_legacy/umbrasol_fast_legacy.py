import sys
import time
from brain_v2 import MonolithSoul
from tools import OperatorInterface

class UmbrasolFast:
    """The Brutal Simplicity Architecture: 95% Zero-AI, 5% Minimal-AI."""
    def __init__(self):
        self.soul = MonolithSoul()
        self.hands = OperatorInterface()
        print("--- Umbrasol: BRUTAL SIMPLICITY MODE ---")
        print("Safety: MAXIMUM | Speed: INSTANT | AI: MINIMAL")

    def execute(self, user_request):
        start = time.time()
        print(f"\n[Request]: {user_request}")
        
        # TIER 1: INSTANT ZERO-AI HEURISTICS (95% of commands)
        req = user_request.lower().strip()
        
        # Direct pattern matching for safety
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
            "show files": ("ls", "."),
            "ls": ("ls", "."),
            "network": ("net", ""),
            "processes": ("proc_list", ""),
        }
        
        for key, (tool, cmd) in instant_map.items():
            if key in req:
                print(f"[INSTANT] Matched: '{key}' -> {tool}")
                result = self._safe_dispatch(tool, cmd)
                print(f"[Result]: {str(result)[:200]}")
                print(f"[Time]: {time.time() - start:.3f}s")
                return
        
        # TIER 2: MINIMAL AI (5% of commands - only for novel requests)
        print("[AI] Novel request detected. Minimal inference...")
        thought = self.soul.execute_task(user_request)
        
        for action in thought.get("actions", []):
            tool = action.get("tool", "stats")
            cmd = action.get("cmd", "")
            result = self._safe_dispatch(tool, cmd)
            print(f"[Result]: {str(result)[:200]}")
        
        print(f"[Time]: {time.time() - start:.3f}s")

    def _safe_dispatch(self, tool, cmd):
        """Execute ONLY whitelisted safe tools."""
        print(f"[Execute]: {tool}({cmd})")
        
        try:
            # SAFETY: Only execute known-safe tools
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
                import threading
                threading.Thread(target=self.hands.gui_speak, args=(cmd,)).start()
                return "Speaking..."
            else:
                return f"BLOCKED: Tool '{tool}' not in safety whitelist"
        except Exception as e:
            return f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/umbrasol_fast.py 'your command'")
        sys.exit(1)
    
    agent = UmbrasolFast()
    agent.execute(sys.argv[1])
