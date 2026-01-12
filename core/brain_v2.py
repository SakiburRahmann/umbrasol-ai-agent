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

    def think_stream(self, prompt, system_prompt="", temperature=0.7, max_tokens=150):
        """Streaming inference for real-time response."""
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n{prompt}",
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_thread": 4,
                "num_ctx": 512
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=60, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("done", False):
                        yield chunk.get("response", "")
        except Exception as e:
            yield f"ERROR: {str(e)}"

class MonolithSoul:
    def __init__(self):
        profiler = HardwareProfiler()
        tier = profiler.get_tier()
        self.model_name = tier['soul']
        self.monolith = Brain(model_name=self.model_name)
        self.memory = ExperienceManager()
        self.safe_tools = settings.SAFE_TOOLS

    def execute_task_stream(self, user_request, context=""):
        """Stream decision and response for real-time interaction."""
        system_name = getattr(settings, "SYSTEM_NAME", "Umbrasol")
        identity = (
            f"You are {system_name}, a highly intelligent digital organism created by Sakibur Rahman. "
            "You possess independent reasoning, logical depth, and a helpful personality. "
            "You are NOT a scripted bot. You think freely and articulately."
        )
        
        lesson = self.memory.get_relevant_lesson(user_request)
        xp_context = f"XP: Previous attempt failed with '{lesson.get('error')}'" if lesson and not lesson.get('success', True) else ""

        prompt = (
            f"System: {identity}\n"
            f"Context: {context}\n"
            f"{xp_context}\n"
            f"User: {user_request}\n\n"
            "DIRECTIVE:\n"
            "1. If the user wants an action (stats, battery, files, window), prefix with 'ACTION: tool,cmd'.\n"
            "2. For ALL other conversation, questions, or analysis, speak naturally. Prefix with 'TALK: '."
        )
        
        full_response = ""
        is_action = False
        buffer = ""
        
        for chunk in self.monolith.think_stream(prompt, system_prompt=identity):
            full_response += chunk
            buffer += chunk
            
            # Detect path as early as possible
            if not is_action and "ACTION:" in full_response:
                is_action = True
                
            if not is_action and "TALK:" in buffer:
                # Yield the conversation bits as they arrive (after the prefix)
                parts = buffer.split("TALK:", 1)
                if len(parts) > 1:
                    yield {"type": "talk", "content": parts[1]}
                    buffer = "" # Clear buffer after yielding current talk segment
            elif not is_action and buffer and len(full_response) > 10:
                # Fallback: if no prefix used but AI started talking
                yield {"type": "talk", "content": buffer}
                buffer = ""

        # Final cleanup for actions
        if is_action:
            parts = full_response.replace("ACTION:", "").strip().split(",", 1)
            tool = parts[0].strip() if len(parts) > 0 else "stats"
            cmd = parts[1].strip() if len(parts) > 1 else ""
            
            if tool not in self.safe_tools: tool = "stats"
            if any(p in cmd.lower() for p in settings.SENSITIVE_PATTERNS): cmd = ""
            
            yield {
                "type": "action",
                "actions": [{"tool": tool, "cmd": cmd}],
                "reasoning": "Action Path"
            }
        else:
            # Yield any remaining buffer
            if buffer:
                yield {"type": "talk", "content": buffer}

    def execute_task(self, user_request, context=""):
        """Non-streaming wrapper for legacy compatibility."""
        results = list(self.execute_task_stream(user_request, context))
        talk_content = "".join([r['content'] for r in results if r['type'] == 'talk'])
        actions = next((r['actions'] for r in results if r['type'] == 'action'), [])
        
        if actions:
            return {"actions": actions, "reasoning": "Action Path", "assessment": "[SAFE]"}
        return {"actions": [], "message": talk_content, "reasoning": "Conversation Path", "assessment": "[TALK]"}
