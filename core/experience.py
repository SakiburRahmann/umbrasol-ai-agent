import json
import os

class ExperienceManager:
    """Layer 7: Chronic Memory. Stores and retrieves lessons from past interactions."""
    def __init__(self, memory_path="config/experience_library.json"):
        self.memory_path = memory_path
        self.memory = self._load()

    def _load(self):
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except: return {}
        return {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=4)
        except: pass

    def save_lesson(self, task, tool, action, error=None):
        """Records a successful pattern or a corrected mistake."""
        key = task.lower().strip()
        lesson = {
            "tool": tool,
            "action": action,
            "error": error,
            "success": error is None
        }
        self.memory[key] = lesson
        self._save()

    def get_relevant_lesson(self, task):
        """Retrieves a past lesson if it exists for this task."""
        key = task.lower().strip()
        return self.memory.get(key)
