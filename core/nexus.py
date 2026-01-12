import sys
import os
import re
import json
import time
from brain import MonolithSoul
from tools import Tools
from cache import SemanticCache
from internet import Internet

class Nexus:
    def __init__(self):
        self.soul = MonolithSoul()
        self.hands = Tools()
        self.cache = SemanticCache()
        self.net = Internet()
        print("--- Project Umbrasol: NEXUS GATEWAY ---")
        print("Status: HYPER-SPEED (Unified Soul Active)")

    def execute(self, user_request):
        start_time = time.time()
        print(f"\n[Nexus]: {user_request}")

        # 1. Semantic Cache Check (Sub-1ms)
        cached = self.cache.get(user_request)
        if cached:
            print("[NEXUS_LINK] High-Confidence Cache Hit.")
            self._run_command(cached['tool'], cached['command'])
            print(f"Total Latency: {time.time() - start_time:.2f}s")
            return

        # 1.5 Hyper-Speed Heuristic (Zero-Inference / Sub-0.1s)
        fast_maps = {
            "list files": ("ls", "."),
            "ls": ("ls", "."),
            "show files": ("ls", "."),
            "system stats": ("stats", ""),
            "cpu usage": ("stats", ""),
            "check ram": ("stats", ""),
            "who am i": ("shell", "whoami"),
            "current dir": ("shell", "pwd")
        }
        
        req_clean = user_request.lower().strip()
        if req_clean in fast_maps:
            print("[NEXUS_FAST] Hyper-Speed Heuristic Match.")
            tool, action = fast_maps[req_clean]
            self._run_command(tool, action)
            print(f"Total Latency: {time.time() - start_time:.2f}s")
            return

        # 2. Speculative Routing (Sub-2s)
        print("[Router] Analyzing intent...")
        route = self.soul.route_task(user_request)
        print(f"[Router] Category: {route}")

        # 3. Execution Path
        if "LITERAL" in route:
            print("[Nexus] Flash-Triage engaged (135M Engine)...")
            thought = self.soul.fast_literal_engine(user_request)
            if not thought:
                print("[Nexus] Flash-Triage failed. Falling back to Monolith...")
                thought = self.soul.execute_task(user_request)
        elif "SEARCH" in route:
            print("[Nexus] Demand-Driven search initializing...")
            # Swift search simulation or actual scrape
            thought = self.soul.execute_task(user_request)
        else:
            print("[Nexus] Complex logic detected. Engaging Monolith...")
            thought = self.soul.execute_task(user_request)

        tool = thought.get("tool", "shell")
        action = thought.get("proposed_action", "")
        assessment = thought.get("assessment", "[SAFE]")
        
        if tool == "DONE" or not action:
            print("[Done] No action needed.")
            return

        # 4. Final Security Check (Internalized)
        print(f"[Security]: {assessment}")
        if "[DANGER]" in assessment.upper():
            print("!!! VETOED: Monolith flagged this as unsafe !!!")
            return

        # 5. Dispatch
        result = self._run_command(tool, action)
        
        # 6. Cache Update (for future instant recall)
        if "ERROR" not in str(result):
            self.cache.set(user_request, tool, action)

        print(f"Total Latency: {time.time() - start_time:.2f}s")

    def _run_command(self, tool, action):
        try:
            print(f"[Action]: {tool}({action})")
            if tool == "shell": result = self.hands.execute_shell(action)
            elif tool == "ls": result = self.hands.list_dir(action if action else ".")
            elif tool == "python": result = self.hands.execute_python(action)
            elif tool == "scrape": result = self.hands.scrape_web(action)
            elif tool == "stats": result = self.hands.get_system_stats()
            else: result = f"ERROR: Tool '{tool}' not supported."
            
            print(f"[Output]: {str(result)[:500]}...")
            return result
        except Exception as e:
            print(f"[Error]: {str(e)}")
            return f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/nexus.py 'query'")
        sys.exit(1)
    agent = Nexus()
    agent.execute(sys.argv[1])
