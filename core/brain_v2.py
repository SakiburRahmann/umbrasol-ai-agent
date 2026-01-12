import requests
import json
import re
from profiler import HardwareProfiler
from experience import ExperienceManager

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
                "num_ctx": 512  # Tiny context for speed
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"ERROR: {str(e)}"

class MonolithSoul:
    def __init__(self):
        profiler = HardwareProfiler()
        tier = profiler.get_tier()
        self.model_name = tier['soul']
        self.router_model = self.model_name
        self.monolith = Brain(model_name=self.model_name)
        self.memory = ExperienceManager()
        
        # SAFETY WHITELIST: Only these tools can be executed
        self.safe_tools = {
            "physical", "existence", "stats", "see_active", "see_tree", 
            "see_raw", "proc_list", "net", "gui_speak", "ls"
        }

    def execute_task(self, user_request, context=""):
        """Minimal AI call with strict safety and Context."""
        
        # Layer 7: Chronic Memory Retrieval
        lesson = self.memory.get_relevant_lesson(user_request)
        xp_context = ""
        if lesson and not lesson.get('success', True):
             xp_context = f"WARNING: Previous attempt failed with '{lesson.get('error')}'. Avoid that."

        # Ultra-compressed prompt
        prompt = (
            f"Context: {context}\n"
            f"XP: {xp_context}\n"
            f"Task: {user_request}\n"
            "Output ONLY: tool,cmd\n"
            "Tools: physical,existence,stats,see_active,ls,gui_speak\n"
            "Example: stats,"
        )
        
        response = self.monolith.think(prompt, max_tokens=30)
        
        # Parse the response
        parts = response.strip().split(",", 1)
        tool = parts[0].strip() if len(parts) > 0 else "stats"
        cmd = parts[1].strip() if len(parts) > 1 else ""
        
        # SAFETY CHECK: Only allow whitelisted tools
        if tool not in self.safe_tools:
            tool = "stats"  # Default to safe
            cmd = ""
        
        # SAFETY CHECK: Block dangerous commands
        dangerous_patterns = ["rm ", "sudo", "dd ", "mkfs", ">", "chmod", "chown"]
        if any(p in cmd.lower() for p in dangerous_patterns):
            cmd = ""
        
        return {
            "actions": [{"tool": tool, "cmd": cmd}],
            "reasoning": "Minimal inference",
            "assessment": "[SAFE]"
        }
