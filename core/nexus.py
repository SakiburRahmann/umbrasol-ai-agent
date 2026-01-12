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
        # (Same as before, but respected by mode)
        cached = self.cache.get(user_request)
        if cached and self.mode == "AUTONOMOUS":
            print("[NEXUS_LINK] High-Confidence Cache Hit.")
            self._dispatch(cached['tool'], cached['command'])
            print(f"Total Latency: {time.time() - start_time:.2f}s")
            return

        # 2. Speculative Routing
        route = self.soul.route_task(user_request)
        
        # 3. Execution Phase
        if "LITERAL" in route:
            thought = self.soul.fast_literal_engine(user_request)
            if not thought: thought = self.soul.execute_task(user_request)
        else:
            thought = self.soul.execute_task(user_request)

        tool = thought.get("tool", "shell")
        action = thought.get("proposed_action", "")
        assessment = thought.get("assessment", "[SAFE]")
        
        # 4. Global Autonomy Shield (Layer 9)
        if self.mode == "MANUAL":
            print(f"\n[APPROVAL_REQUIRED]: {tool}({action})")
            confirm = input("Proceed? (y/n): ")
            if confirm.lower() != 'y': return
        elif self.mode == "ASSISTED" and ("[DANGER]" in assessment or self.hands.is_sensitive(action)):
            print(f"\n[SECURITY_CONFIRMATION]: {tool}({action})")
            confirm = input("This action is sensitive. Proceed? (y/n): ")
            if confirm.lower() != 'y': return

        # 5. Dispatch
        self._dispatch(tool, action)
        print(f"Total Latency: {time.time() - start_time:.2f}s")

    def _dispatch(self, tool, action):
        if self.simulate:
            print(f"[SIMULATION]: Would execute {tool}({action})")
            return
            
        print(f"[Action]: {tool}({action})")
        # Logic for execution...
        try:
            if tool == "shell": result = self.hands.execute_shell(action)
            elif tool == "stats": result = self.hands.get_system_stats()
            elif tool == "existence": result = self.hands.get_existence_stats()
            elif tool == "physical": result = self.hands.get_physical_state()
            elif tool == "power": result = self.hands.manage_power(action)
            elif tool == "health": result = self.hands.proactive_maintenance()
            elif tool == "proc_list": result = self.hands.get_process_list()
            elif tool == "kill": result = self.hands.kill_process(int(action))
            elif tool == "net": result = self.hands.get_network_stats()
            elif tool == "see": result = self.hands.ui_perception()
            # ... other tools
            print(f"[Output]: {str(result)[:500]}")
        except Exception as e:
            print(f"[Error]: {str(e)}")
            return f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/nexus.py 'query'")
        sys.exit(1)
    agent = Nexus()
    agent.execute(sys.argv[1])
