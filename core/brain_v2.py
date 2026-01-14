import httpx
import json
import os
import re
import logging
from core.profiler import HardwareProfiler
from core.experience import ExperienceManager
from config import settings

class Brain:
    def __init__(self, model_name="qwen2.5:3b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"
        self.logger = logging.getLogger("Umbrasol.Brain")

    async def think_stream(self, prompt, system_prompt="", temperature=0.7, max_tokens=300, format=None):
        """Async streaming inference using httpx."""
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n{prompt}",
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_thread": os.cpu_count() or 4,
                "num_ctx": 4096
            }
        }
        if format:
            payload["format"] = format

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", self.base_url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            chunk = json.loads(line)
                            if chunk.get("done", False):
                                break
                            yield chunk.get("response", "")
        except Exception as e:
            self.logger.error(f"Brain Error: {e}")
            yield f"ERROR: {str(e)}"

class MonolithSoul:
    def __init__(self, override_model=None):
        profiler = HardwareProfiler()
        tier = profiler.get_tier()
        self.model_name = override_model or tier['soul']
        self.monolith = Brain(model_name=self.model_name)
        self.memory = ExperienceManager()
        self.safe_tools = settings.SAFE_TOOLS
        self.logger = logging.getLogger("Umbrasol.Soul")

    async def execute_task_stream(self, user_request, context=""):
        """Stream decision and response using a robust prefix-based protocol."""
        system_name = getattr(settings, "SYSTEM_NAME", "Umbrasol")
        
        identity = (
            f"You are {system_name}, an autonomous local AI agent. "
            "You are witty, concise, and articulate. "
            "You MUST use these prefixes: REASONING: (internal thought), TALK: (to user), ACTION: tool,cmd (to act)."
        )
        
        tool_desc = (
            "net: swift_search (web news); stats: cpu/ram; see_active: window; "
            "ls/shell: files/system control; gui_speak: speak text."
        )

        prompt = (
            f"Context: {context}\n"
            f"User: {user_request}\n\n"
            f"Tools: {tool_desc}\n"
            "Format:\n"
            "REASONING: Why you chose this.\n"
            "TALK: Your message.\n"
            "ACTION: tool,query"
        )

        full_response = ""
        last_pos = 0
        current_type = None # reasoning, talk, action

        async for chunk in self.monolith.think_stream(prompt, system_prompt=identity, temperature=0.3, max_tokens=600):
            full_response += chunk
            
            # Identify current segment
            if "REASONING:" in full_response[last_pos:] and current_type != "reasoning":
                current_type = "reasoning"
                res_idx = full_response.find("REASONING:", last_pos)
                last_pos = res_idx + 10
            elif "TALK:" in full_response[last_pos:] and current_type != "talk":
                current_type = "talk"
                talk_idx = full_response.find("TALK:", last_pos)
                last_pos = talk_idx + 5
            elif "ACTION:" in full_response[last_pos:] and current_type != "action":
                current_type = "action"
                act_idx = full_response.find("ACTION:", last_pos)
                last_pos = act_idx + 7

            # Yield based on type
            if current_type == "talk":
                new_text = full_response[last_pos:]
                if "ACTION:" not in new_text:
                    yield {"type": "talk", "content": new_text}
                    last_pos = len(full_response)
            elif current_type == "reasoning":
                new_text = full_response[last_pos:]
                if "TALK:" not in new_text and "ACTION:" not in new_text:
                    yield {"type": "reasoning", "content": new_text}
                    last_pos = len(full_response)

        # FINAL ACTION PARSING
        import re
        ACTION_PATTERN = re.compile(r"ACTION:\s*([^,\n]*),\s*(.*)", re.IGNORECASE)
        actions = []
        for match in ACTION_PATTERN.finditer(full_response):
            tool = match.group(1).strip().lower()
            cmd = match.group(2).strip().split("TALK:")[0].strip()
            
            # Fuzzy match
            if tool not in self.safe_tools:
                for t in self.safe_tools:
                    if tool in t or t in tool: tool = t; break
                else: tool = "stats"
            
            actions.append({"tool": tool, "cmd": cmd})

        if actions:
            yield {"type": "action", "actions": actions}

    async def execute_task(self, user_request, context=""):
        """Non-streaming wrapper."""
        results = []
        async for res in self.execute_task_stream(user_request, context):
            results.append(res)
            
        talk_content = "".join([r['content'] for r in results if r['type'] == 'talk'])
        actions = []
        for r in results:
            if r['type'] == 'action':
                actions.extend(r.get('actions', []))
        
        return {
            "actions": actions, 
            "message": talk_content, 
            "reasoning": "Standard Path", 
            "assessment": "[SAFE]" if actions else "[TALK]"
        }
