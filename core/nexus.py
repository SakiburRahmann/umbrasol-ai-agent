import sys
import os
import re
import json
import time
from brain import MonolithSoul
from tools import OperatorInterface
from cache import SemanticCache
from internet import Internet

class Nexus:
    def __init__(self, mode="ASSISTED", simulate=False):
        self.soul = MonolithSoul()
        self.hands = OperatorInterface()
        self.cache = SemanticCache()
        self.net = Internet()
        self.mode = mode # MANUAL, ASSISTED, AUTONOMOUS
        self.simulate = simulate
        print("--- Project Umbrasol: NEXUS GATEWAY ---")
        print(f"Status: DIGITAL OPERATOR | Mode: {self.mode} | Simulate: {self.simulate}")

    def execute(self, user_request):
        start_time = time.time()
        print(f"\n[Nexus]: {user_request}")

        # 1. Semantic Cache Check (Sub-1ms)
        cached = self.cache.get(user_request)
        if cached and self.mode == "AUTONOMOUS":
            print("[NEXUS_LINK] High-Confidence Cache Hit.")
            self._dispatch(cached['tool'], cached['command'], user_request)
            print(f"Total Latency: {time.time() - start_time:.2f}s")
            return

        # 1.5 Hyper-Speed Heuristic (Zero-Inference / Sub-0.1s)
        # Bypasses BOTH models for known system intents.
        req_clean = user_request.lower().strip().replace("?", "")
        
        # Keyword-based Fast-Map (More robust than exact matches)
        fast_triggers = {
            "battery": ("physical", ""),
            "power": ("physical", ""),
            "charge": ("physical", ""),
            "thermal": ("physical", ""),
            "temp": ("physical", ""),
            "uptime": ("existence", ""),
            "who am i": ("shell", "whoami"),
            "current dir": ("shell", "pwd"),
            "ram": ("stats", ""),
            "memory": ("stats", ""),
            "cpu": ("stats", ""),
            "process": ("proc_list", ""),
            "active window": ("see_active", ""),
            "what window": ("see_active", ""),
            "active tab": ("see_active", ""),
            "list files": ("ls", "."),
            "ls": ("ls", "."),
            "show files": ("ls", "."),
            "network": ("net", ""),
            "net": ("net", ""),
            "health": ("health", "")
        }
        
        for key, (tool, action) in fast_triggers.items():
            if key in req_clean:
                print(f"[NEXUS_FAST] Hyper-Speed Heuristic Match: '{key}' (0.00s Bypass).")
                self._dispatch(tool, action, user_request)
                print(f"Total Latency: {time.time() - start_time:.2f}s")
                return

        executed_actions = []
        def eager_dispatch(plan):
            tool = plan.get("tool")
            cmd = plan.get("cmd")
            if (tool, cmd) not in executed_actions:
                self._dispatch(tool, cmd, user_request)
                executed_actions.append((tool, cmd))

        # 2. Execution Phase (Eager Mono-Soul)
        if self.soul.router_model == self.soul.model_name:
            print("[NEXUS] Mono-Soul Active. Eager Pulse initialized.")
            thought = self.soul.execute_task(user_request, callback=eager_dispatch)
        else:
            route = self.soul.route_task(user_request)
            if "LITERAL" in route:
                thought = self.soul.fast_literal_engine(user_request)
                if not thought: thought = self.soul.execute_task(user_request, callback=eager_dispatch)
                else: eager_dispatch(thought)
            else:
                thought = self.soul.execute_task(user_request, callback=eager_dispatch)

        # Ensure everything in thought['actions'] was handled
        for action in thought.get("actions", []):
            eager_dispatch(action)

        print(f"Total Time-to-Action: {time.time() - start_time:.2f}s")

    def _dispatch(self, tool, action, user_request=None):
        if self.simulate:
            print(f"[SIMULATION]: {tool}({action})")
            return
            
        # Parallel Execution for specific non-critical tasks (Communication)
        if tool == "gui_speak":
            import threading
            print(f"[Action]: {tool}({action}) [BKGND]")
            threading.Thread(target=self.hands.gui_speak, args=(action,)).start()
            return "SUCCESS: Speaking in background."

        print(f"[Action]: {tool}({action})")
        try:
            result = "ERROR: No action"
            # Specialized dispatcher logic...
            dispatch_map = {
                "shell": self.hands.execute_shell,
                "ls": self.hands.list_dir,
                "stats": self.hands.get_system_stats,
                "existence": self.hands.get_existence_stats,
                "physical": self.hands.get_physical_state,
                "power": self.hands.manage_power,
                "health": self.hands.proactive_maintenance,
                "see_raw": self.hands.capture_screen,
                "see_tree": self.hands.observe_ui_tree,
                "see_meta": self.hands.get_window_metadata,
                "see_active": self.hands.read_active_window,
                "proc_list": self.hands.get_process_list,
                "kill": lambda a: self.hands.kill_process(int(a)),
                "net": self.hands.get_network_stats,
                "gui_type": self.hands.gui_type,
                "gui_scroll": self.hands.gui_scroll
            }
            
            if tool in dispatch_map:
                result = dispatch_map[tool](action) if action else dispatch_map[tool]()
            elif tool == "gui_click":
                coords = action.split()
                result = self.hands.gui_click(coords[0], coords[1]) if len(coords) >= 2 else "ERROR: Missing Coords"
            elif tool == "python":
                result = self.hands.execute_shell(f"python3 -c '{action}'")
            
            # Layer 7: Commit to Memory
            if user_request: self.soul.memory.save_lesson(user_request, tool, action, error=None if "ERROR" not in str(result) else str(result))
            
            print(f"[Output]: {str(result)[:200]}...")
            return result
        except Exception as e:
            return f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/nexus.py 'query'")
        sys.exit(1)
    agent = Nexus()
    agent.execute(sys.argv[1])
