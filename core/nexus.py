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

        # 2. Execution Phase (Optimized for Mono-Soul)
        if self.soul.router_model == self.soul.model_name:
            # Mono-Soul Logic: Skip redundant routing call (Save ~20s)
            print("[NEXUS] Mono-Soul Active. Directing request to Monolith.")
            thought = self.soul.execute_task(user_request)
        else:
            # Multi-Soul Logic: Triage with 135M first
            route = self.soul.route_task(user_request)
            if "LITERAL" in route:
                thought = self.soul.fast_literal_engine(user_request)
                if not thought: thought = self.soul.execute_task(user_request)
            else:
                thought = self.soul.execute_task(user_request)

        for attempt in range(2): # Allow 1 automatic correction attempt
            tool = thought.get("tool", "shell")
            action = thought.get("proposed_action", "")
            assessment = thought.get("assessment", "[SAFE]")
            
            # 4. Global Autonomy Shield (Layer 9)
            # ... (skipped for core logic)
            
            # 5. Dispatch
            result = self._dispatch(tool, action, user_request)
            
            # Layer 8: Self-Correction (True Learning)
            is_error = False
            error_msg = ""
            if isinstance(result, str) and "ERROR" in result.upper():
                is_error = True
                error_msg = result
            elif isinstance(result, dict) and result.get("exit_code", 0) != 0:
                is_error = True
                error_msg = result.get("output", "Return code non-zero")

            if is_error and attempt == 0:
                print(f"[Learning] Analysis of failure: {error_msg[:100]}...")
                # Re-wake the soul with the failure context
                error_context = f"Your previous attempt {tool}({action}) FAILED with error: {error_msg}. Avoid this and try a different approach."
                thought = self.soul.execute_task(user_request + f"\n[RETRY_CONTEXT: {error_context}]")
                continue 
            else:
                break 
        
        print(f"Total Latency: {time.time() - start_time:.2f}s")

    def _dispatch(self, tool, action, user_request=None):
        if self.simulate:
            print(f"[SIMULATION]: Would execute {tool}({action})")
            return
            
        print(f"[Action]: {tool}({action})")
        # Logic for execution...
        try:
            result = "ERROR: No action"
            if tool == "shell": result = self.hands.execute_shell(action)
            elif tool == "ls": result = self.hands.list_dir(action)
            elif tool == "python": result = self.hands.execute_shell(f"python3 -c '{action}'")
            elif tool == "stats": result = self.hands.get_system_stats()
            elif tool == "existence": result = self.hands.get_existence_stats()
            elif tool == "physical": result = self.hands.get_physical_state()
            elif tool == "power": result = self.hands.manage_power(action)
            elif tool == "health": result = self.hands.proactive_maintenance()
            elif tool == "see_raw": result = self.hands.capture_screen()
            elif tool == "see_tree": result = self.hands.observe_ui_tree()
            elif tool == "see_meta": result = self.hands.get_window_metadata(action)
            elif tool == "see_active": result = self.hands.read_active_window()
            elif tool == "proc_list": result = self.hands.get_process_list()
            elif tool == "kill": result = self.hands.kill_process(int(action))
            elif tool == "net": result = self.hands.get_network_stats()
            elif tool == "gui_click": 
                coords = action.split()
                if len(coords) >= 2: result = self.hands.gui_click(coords[0], coords[1])
                else: result = "ERROR: Coordinates missing for click"
            elif tool == "gui_type": result = self.hands.gui_type(action)
            elif tool == "gui_scroll": result = self.hands.gui_scroll(action)
            elif tool == "gui_speak": result = self.hands.gui_speak(action)
            # ... other tools
            
            error = None
            if isinstance(result, str) and "ERROR" in result: 
                error = result
            elif isinstance(result, dict) and result.get("exit_code", 0) != 0:
                error = result.get("output", "Unknown Error")
            
            # Layer 7: Commit to Chronic Memory
            if user_request:
                self.soul.memory.save_lesson(user_request, tool, action, error=error)
                
            print(f"[Output]: {str(result)[:500]}")
            return result
        except Exception as e:
            msg = f"ERROR: {str(e)}"
            if user_request:
                self.soul.memory.save_lesson(user_request, tool, action, error=msg)
            print(f"[Error]: {msg}")
            return msg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/nexus.py 'query'")
        sys.exit(1)
    agent = Nexus()
    agent.execute(sys.argv[1])
