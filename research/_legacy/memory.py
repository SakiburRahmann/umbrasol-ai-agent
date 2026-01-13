import json
import os
import time

class Memory:
    def __init__(self, base_dir="memory"):
        self.base_dir = base_dir
        self.scratchpad_path = os.path.join(base_dir, "scratchpad.json")
        self.life_diary_path = os.path.join(base_dir, "life_diary.json")
        
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
        self._init_files()

    def _init_files(self):
        if not os.path.exists(self.scratchpad_path):
            self.clear_scratchpad()
        if not os.path.exists(self.life_diary_path):
            with open(self.life_diary_path, 'w') as f:
                json.dump({"permanent_facts": []}, f)

    def clear_scratchpad(self):
        """Reset the temporary memory for a new task."""
        data = {
            "task": "",
            "start_time": time.time(),
            "steps": [],
            "summary": "Initializing task..."
        }
        with open(self.scratchpad_path, 'w') as f:
            json.dump(data, f, indent=4)

    def update_scratchpad(self, step_name, reasoning, command, result, status="success"):
        """Add a step to the current task execution."""
        with open(self.scratchpad_path, 'r') as f:
            data = json.load(f)
            
        step_entry = {
            "timestamp": time.time(),
            "step": step_name,
            "reasoning": reasoning,
            "command": command,
            "result": str(result),
            "status": status
        }
        
        data["steps"].append(step_entry)
        
        # Context Distillation: Summarize current progress to keep context lean
        data["summary"] = f"Completed {len(data['steps'])} steps. Last action: {step_name} ({status})."
        
        with open(self.scratchpad_path, 'w') as f:
            json.dump(data, f, indent=4)

    def search_scratchpad(self):
        """Returns the condensed history for the LLM context."""
        with open(self.scratchpad_path, 'r') as f:
            data = json.load(f)
            
        context = f"CURRENT TASK: {data['task']}\nPROGRESS: {data['summary']}\n"
        context += "PAST STEPS:\n"
        for step in data["steps"]:
            context += f"- {step['step']}: {step['status']}\n"
            
        return context

    def promote_to_diary(self, fact, significance):
        """Adds important knowledge to permanent memory if significance >= 8."""
        if significance < 8:
            return False
            
        with open(self.life_diary_path, 'r') as f:
            diary = json.load(f)
            
        entry = {
            "fact": fact,
            "learned_at": time.ctime(),
            "significance": significance
        }
        
        diary["permanent_facts"].append(entry)
        
        with open(self.life_diary_path, 'w') as f:
            json.dump(diary, f, indent=4)
        return True

    def get_chronic_memory(self):
        """Returns all permanent facts stored in the life diary."""
        with open(self.life_diary_path, 'r') as f:
            diary = json.load(f)
        return "\n".join([f"- {f['fact']}" for f in diary["permanent_facts"]])

if __name__ == "__main__":
    mem = Memory()
    mem.promote_to_diary("User prefers Python for automation.", 9)
    print("Chronic Memory:\n", mem.get_chronic_memory())
