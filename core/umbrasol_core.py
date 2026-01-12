import sys
import os
from brain import DualSoul
from tools import Tools

class Umbrasol:
    def __init__(self):
        self.soul = DualSoul()
        self.hands = Tools()
        print("--- Project Umbrasol Initialized ---")
        print("Status: GHOST MODE ACTIVE")

    def run(self, task_description):
        print(f"\n[Task Request]: {task_description}")
        
        # 1. Thinking Phase
        print("[Thinking] Brain 1 (Doer) generating strategy...")
        result = self.soul.execute_task(task_description)
        
        proposed_action = result["proposed_action"]
        assessment = result["assessment"]
        
        print(f"\n[Proposed Action]:\n{proposed_action}")
        print(f"\n[Guardian Assessment]:\n{assessment}")
        
        # 2. Safety Gate
        if "[DANGER]" in assessment.upper():
            print("\n!!! SECURITY BLOCK !!!")
            print("The Guardian soul has vetoed this action.")
            return
        
        if "[SAFE]" not in assessment.upper():
            print("\n[Warning]: Assessment unclear. Aborting for safety.")
            return

        # 3. Execution Phase
        print("\n[Execution] Proceeding with action...")
        # For the prototype, we assume the Doer outputs a single or block of commands
        execution_result = self.hands.execute_shell(proposed_action)
        
        print("\n[Execution Result]:")
        print(execution_result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chimera_core.py 'your task here'")
        sys.exit(1)
        
    task = sys.argv[1]
    agent = Umbrasol()
    agent.run(task)
