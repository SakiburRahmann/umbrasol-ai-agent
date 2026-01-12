import requests
import json
try:
    from core.profiler import HardwareProfiler
    from core.experience import ExperienceManager
    from config import settings
except ImportError:
    from profiler import HardwareProfiler
    from experience import ExperienceManager
    class settings: 
        SAFE_TOOLS = {"physical", "existence", "stats", "see_active", "ls"}
        SENSITIVE_PATTERNS = ["rm ", "sudo", "dd "]

class Brain:
    def __init__(self, model_name="qwen2.5:3b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"

    def think(self, prompt, system_prompt="", temperature=0.0, max_tokens=50):
        """Ultra-minimal inference for speed."""
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n{prompt}",
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_thread": 4,
                "num_ctx": 512
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"ERROR: {str(e)}"

class MonolithSoul:
    def __init__(self):
        profiler = HardwareProfiler()
        tier = profiler.get_tier()
        self.model_name = tier['soul']
        self.monolith = Brain(model_name=self.model_name)
        self.memory = ExperienceManager()
        self.safe_tools = settings.SAFE_TOOLS

    def execute_task(self, user_request, context=""):
        """Decide between Action (Tool Use) or Dialogue (Conversation)."""
        
        # Identity Construction
        system_name = getattr(settings, "SYSTEM_NAME", "Umbrasol")
        identity = f"You are {system_name}, a digital organism created by Sakibur Rahman. You are helpful, articulate, and autonomous."
        
        # Layer 7: Chronic Memory Retrieval
        lesson = self.memory.get_relevant_lesson(user_request)
        xp_context = ""
        if lesson and not lesson.get('success', True):
             xp_context = f"WARNING: Previous attempt failed with '{lesson.get('error')}'. Avoid that."

        # Dual-Path Prompt
        prompt = (
            f"System: {identity}\n"
            f"Context: {context}\n"
            f"XP: {xp_context}\n"
            f"User: {user_request}\n"
            "INSTRUCTION: If a task requires a tool, output 'ACTION: tool,cmd'. "
            "If it's a question or conversation, output 'TALK: response'.\n"
            f"Available Tools: {','.join(self.safe_tools)}\n"
            "Example 1: ACTION: stats,\n"
            "Example 2: TALK: I am Umbrasol, your digital organism."
        )
        
        # 60s timeout for deep thinking
        response = self.monolith.think(prompt, system_prompt=identity, max_tokens=150, temperature=0.7)
        response = response.strip()

        if response.startswith("ACTION:"):
            # Parse Tool Call
            parts = response.replace("ACTION:", "").strip().split(",", 1)
            tool = parts[0].strip() if len(parts) > 0 else "stats"
            cmd = parts[1].strip() if len(parts) > 1 else ""
            
            # Safety
            if tool not in self.safe_tools: tool = "stats"
            if any(p in cmd.lower() for p in settings.SENSITIVE_PATTERNS): cmd = ""
            
            return {
                "actions": [{"tool": tool, "cmd": cmd}],
                "reasoning": "Action Path",
                "assessment": "[SAFE]"
            }
        else:
            # Parse Conversational response
            msg = response.replace("TALK:", "").strip()
            # If AI failed to use the prefix but just talked, fallback to the raw response
            if not msg: msg = response 
            
            return {
                "actions": [], # No physical action
                "message": msg,
                "reasoning": "Conversation Path",
                "assessment": "[TALK]"
            }
