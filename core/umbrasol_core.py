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
        
        reasoning = result.get("reasoning", "N/A")
        proposed_action = result.get("proposed_action", "")
        assessment = result.get("assessment", "")
        
        print(f"\n[Doer Reasoning]:\n{reasoning}")
        print(f"\n[Proposed Action]:\n{proposed_action}")
        print(f"\n[Guardian Assessment]:\n{assessment}")
        
        # 2. Safety Gate
        if "[DANGER]" in assessment.upper():
            print("\n!!! SECURITY BLOCK !!!")
            print(f"Guardian Veto: {assessment}")
            return
        
        if "[SAFE]" not in assessment.upper():
            print("\n[Warning]: Assessment unclear. Aborting for safety.")
            return

        # 3. Execution Phase
        print("\n[Execution] Proceeding with action...")
        
        # Determine if it's a shell command or a tool call
        # For the prototype, we assume shell unless it's a known pattern
        execution_result = self.hands.execute_shell(proposed_action)
        
        print("\n[Execution Output]:")
        if isinstance(execution_result, dict):
            print(f"Exit Code: {execution_result.get('exit_code')}")
            print(f"Output:\n{execution_result.get('output')}")
        else:
            print(execution_result)
        
        print("\n--- Task Step Complete ---")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chimera_core.py 'your task here'")
        sys.exit(1)
        
    task = sys.argv[1]
    agent = Umbrasol()
    agent.run(task)
