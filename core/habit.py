import os
import time
from datetime import datetime
from core.omega_memory import OmegaMemory

class HabitManager:
    """
    Layer 4: Habit Modeling (Subconscious Loop).
    Learns user patterns based on Time of Day + Active Context.
    """
    def __init__(self, memory=None):
        self.memory = memory or OmegaMemory()

    def _get_time_slot(self):
        """Returns: Morning, Afternoon, Evening, Night"""
        h = datetime.now().hour
        if 5 <= h < 12: return "Morning"
        elif 12 <= h < 17: return "Afternoon"
        elif 17 <= h < 22: return "Evening"
        else: return "Night"

    async def learn(self, active_window, command):
        """Records a habit: When [Time] in [App] -> User did [Command]."""
        slot = self._get_time_slot()
        app_name = "Unknown"
        if active_window:
             parts = active_window.split("-")
             app_name = parts[-1].strip() if len(parts) > 1 else str(active_window)[:20]
        
        context_key = f"{slot}|{app_name}"
        habits = await self.memory.get_habit(context_key)
        
        cmd_key = str(command)
        habits[cmd_key] = habits.get(cmd_key, 0) + 1
        await self.memory.save_habit(context_key, habits)

    async def predict(self, active_window, threshold=3):
        """Returns a likely command if confidence > threshold."""
        slot = self._get_time_slot()
        app_name = "Unknown"
        if active_window:
             parts = active_window.split("-")
             app_name = parts[-1].strip() if len(parts) > 1 else str(active_window)[:20]

        context_key = f"{slot}|{app_name}"
        habits = await self.memory.get_habit(context_key)
        
        if habits:
            best_cmd = max(habits, key=habits.get)
            count = habits[best_cmd]
            
            if count >= threshold:
                return best_cmd, count
        
        return None, 0
