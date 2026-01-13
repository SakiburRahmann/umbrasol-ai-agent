import os
from core.omega_memory import OmegaMemory

class ExperienceManager:
    """Layer 7: Chronic Memory. Stores and retrieves lessons from past interactions."""
    def __init__(self, memory=None):
        self.memory = memory or OmegaMemory()

    def save_lesson(self, task, tool, action, error=None):
        """Records a successful pattern or a corrected mistake."""
        task_key = task.lower().strip()
        lesson = {
            "tool": tool,
            "action": action,
            "error": error,
            "success": error is None
        }
        self.memory.save_experience(task_key, lesson)

    def get_relevant_lesson(self, task):
        """Retrieves a past lesson if it exists for this task."""
        task_key = task.lower().strip()
        return self.memory.get_experience(task_key)
