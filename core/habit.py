import json
import os
import time
from datetime import datetime

class HabitManager:
    """
    Layer 4: Habit Modeling (Subconscious Loop).
    Learns user patterns based on Time of Day + Active Context.
    """
    def __init__(self, habit_path="config/habit_memory.json"):
        self.habit_path = habit_path
        self.habits = self._load()

    def _load(self):
        if os.path.exists(self.habit_path):
            try:
                with open(self.habit_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"HabitManager Error: Could not load habits: {e}")
                return {}
        return {}

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.habit_path), exist_ok=True)
            with open(self.habit_path, 'w') as f:
                json.dump(self.habits, f, indent=4)
        except Exception as e:
            print(f"HabitManager Error: Could not save habits: {e}")

    def _get_time_slot(self):
        """Returns: Morning, Afternoon, Evening, Night"""
        h = datetime.now().hour
        if 5 <= h < 12: return "Morning"
        elif 12 <= h < 17: return "Afternoon"
        elif 17 <= h < 22: return "Evening"
        else: return "Night"

    def learn(self, active_window, command):
        """Records a habit: When [Time] in [App] -> User did [Command]."""
        slot = self._get_time_slot()
        # Clean context to just the app name if possible, simplifies key
        app_name = "Unknown"
        if active_window:
             # Heuristic: "code - core/habit.py" -> "code"
             parts = active_window.split("-")
             app_name = parts[-1].strip() if len(parts) > 1 else str(active_window)[:20]
        
        key = f"{slot}|{app_name}"
        
        if key not in self.habits:
            self.habits[key] = {}
        
        cmd_key = str(command) # Could be a dict or string
        if cmd_key not in self.habits[key]:
            self.habits[key][cmd_key] = 0
        
        self.habits[key][cmd_key] += 1
        self._save()

    def predict(self, active_window, threshold=3):
        """Returns a likely command if confidence > threshold."""
        slot = self._get_time_slot()
        app_name = "Unknown"
        if active_window:
             parts = active_window.split("-")
             app_name = parts[-1].strip() if len(parts) > 1 else str(active_window)[:20]

        key = f"{slot}|{app_name}"
        if key in self.habits:
            # Find command with highest count
            best_cmd = max(self.habits[key], key=self.habits[key].get)
            count = self.habits[key][best_cmd]
            
            if count >= threshold:
                return best_cmd, count
        
        return None, 0
