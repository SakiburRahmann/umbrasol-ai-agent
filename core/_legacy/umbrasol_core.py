import sys
import os
import time
from brain import MonolithSoul
from tools import OperatorInterface
from memory import Memory
from internet import Internet

class Umbrasol:
    def __init__(self):
        self.soul = MonolithSoul()
        self.hands = OperatorInterface()
        self.memory = Memory()
        self.net = Internet()
        print("--- Project Umbrasol: LITE CORE ---")
        print("Status: SPEED OPTIMIZED (Unified Soul Active)")

    def run(self, task_description, max_steps=5):
        print(f"\n[REQUEST]: {task_description}")
        self.memory.clear_scratchpad()
        
        # Umbrasol Lite: No automatic pre-search. 
        # The agent searches only if it chooses to use the 'scrape' tool.

        for step in range(1, max_steps + 1):
            print(f"\n--- Cycle {step} ---")
            
            # Context Optimization: Only feed distilled scratchpad to save tokens
            scratchpad = self.memory.search_scratchpad()
            chronic = self.memory.get_chronic_memory()
            
            # Thinking Phase
            thought = self.soul.execute_task(task_description, scratchpad, chronic)
            
            tool = thought.get("tool", "shell")
            action = thought.get("proposed_action", "")
            reasoning = thought.get("reasoning", "Thinking...")
            importance = thought.get("importance", 0)
            
            if tool == "DONE" or not action:
                print("\n[Complete] Goal achieved.")
                break
                
            print(f"[Plan]: {reasoning}")
            print(f"[Tool]: {tool} | [Action]: {action}")
            
            # --- INTERNALIZED SAFETY (Phase 3.5 Logic) ---
            print(f"[Security]: {assessment}")
            
            if "[DANGER]" in assessment.upper():
                print("!!! VETOED: Monolith flagged this as unsafe !!!")
                self.memory.update_scratchpad(f"Cycle_{step}", reasoning, f"{tool}:{action}", "BLOCKED", "failed")
                continue
            
            # Execution
            try:
                if tool == "shell": result = self.hands.execute_shell(action)
                elif tool == "python": result = self.hands.execute_python(action)
                elif tool == "scrape": result = self.hands.scrape_web(action)
                elif tool == "ls": result = self.hands.list_dir(action if action else ".")
                elif tool == "cd": result = self.hands.change_dir(action)
                elif tool == "edit":
                    if "|" in action:
                        p, l, c = action.split('|', 2)
                        result = self.hands.edit_line(p, int(l), c)
                    else: result = "ERROR: Format p|l|c"
                else: result = f"ERROR: Unknown tool '{tool}'"
            except Exception as e:
                result = f"EXEC_ERR: {str(e)}"
            
            print(f"[Output]: {str(result)[:60]}...")
            self.memory.update_scratchpad(f"Cycle_{step}", reasoning, f"{tool}:{action}", str(result))
            
            if importance >= 9:
                self.memory.promote_to_diary(f"{task_description}: {reasoning}", importance)

        print("\n--- Mission Ended ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python core/umbrasol_core.py 'query'")
        sys.exit(1)
    agent = Umbrasol()
    agent.run(sys.argv[1])
