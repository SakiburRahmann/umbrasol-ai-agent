import sys
import os
import re
import json
from brain import MonolithSoul
from tools import Tools

class Switchblade:
    def __init__(self):
        self.soul = MonolithSoul()
        self.hands = Tools()
        print("--- Project Umbrasol: SWITCHBLADE CORE ---")
        print("Mode: HIGH-SPEED (Monolith-Prime Active)")

    def execute(self, user_request):
        print(f"\n[Direct]: {user_request}")
        
        # 1. Single-Step Thinking (Unified Soul)
        thought = self.soul.execute_task(user_request)
        
        tool = thought.get("tool", "shell")
        action = thought.get("proposed_action", "")
        
        if tool == "DONE" or not action:
            print("[Done] No action needed.")
            return

        print(f"[Action]: {tool}({action})")

        # 2. Final Security Check (Internalized)
        assessment = thought.get("assessment", "[SAFE]")
        print(f"[Security]: {assessment}")

        if "[DANGER]" in assessment.upper():
            print("!!! VETOED: Monolith flagged this as unsafe !!!")
            return

        # 4. Immediate Execution
        try:
            if tool == "shell": result = self.hands.execute_shell(action)
            elif tool == "ls": result = self.hands.list_dir(action if action else ".")
            elif tool == "python": result = self.hands.execute_python(action)
            elif tool == "scrape": result = self.hands.scrape_web(action)
            elif tool == "edit":
                # Expects path|line|content
                if "|" in action:
                    p, l, c = action.split("|", 2)
                    result = self.hands.edit_line(p, int(l), c)
                else: result = "ERROR: Fast-edit requires 'path|line|content' format."
            elif tool == "stats": result = self.hands.get_system_stats()
            else: result = f"ERROR: Fast-core doesn't support '{tool}' yet."
            
            print(f"[Output]: {str(result)[:500]}...")
        except Exception as e:
            print(f"[Error]: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/umbrasol_fast.py 'query'")
        sys.exit(1)
    agent = Switchblade()
    agent.execute(sys.argv[1])
