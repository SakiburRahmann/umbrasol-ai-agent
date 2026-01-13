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
            "2. For ALL other conversation, speak naturally in full paragraphs. Prefix with 'TALK: '.\n"
            "CRITICAL: DO NOT use markdown symbols (**, #, _, *). DO NOT use numbered or bulleted lists. "
            "DO NOT say 'AI:' or 'Human:'. Speak as a human would in a natural, flowing conversation."
        )
        
        import re
        full_response = ""
        action_yielded = False
        
        # Regex Patterns
        ACTION_PATTERN = re.compile(r"ACTION:\s*([^,\n]*),\s*(.*)", re.IGNORECASE)
        TALK_PATTERN = re.compile(r"TALK:\s*(.*)", re.IGNORECASE | re.DOTALL)

        for chunk in self.monolith.think_stream(prompt, system_prompt=identity):
            full_response += chunk
            
            # 1. Immediate Talk Response (Streaming sentences)
            # Find all Talk segments NOT followed by an Action
            if "TALK:" in full_response:
                # Extract text between TALK: and either the next ACTION: or end of string
                talk_segments = re.findall(r"TALK:\s*(.*?)(?=ACTION:|TALK:|$)", full_response, re.DOTALL | re.IGNORECASE)
                # We yield the latest segment if it looks complete
                if talk_segments:
                    latest = talk_segments[-1].strip()
                    # Basic sentence/pause detection to avoid stutter
                    if any(p in latest for p in [".", "!", "?", "\n"]):
                        # Only yield what we haven't yielded yet
                        # (This streaming logic is simplified; for a real production app we'd track offsets)
                        pass

        # POST-STREAM PARSING (ROBUST)
        # We parse the full response at the end for finality
        # 1. Extract Actions
        action_match = ACTION_PATTERN.search(full_response)
        if action_match:
            tool = action_match.group(1).strip()
            cmd = action_match.group(2).strip()
            
            # Clean cmd of potential trailing 'TALK:' or markdown
            cmd = re.split(r"TALK:", cmd, flags=re.IGNORECASE)[0].strip()
            
            if tool not in self.safe_tools: tool = "stats"
            if any(p in cmd.lower() for p in settings.SENSITIVE_PATTERNS): cmd = ""
            
            yield {
                "type": "action",
                "actions": [{"tool": tool, "cmd": cmd}],
                "reasoning": "Standard Action Path"
            }

        # 2. Extract Talk
        # Get everything flagged as TALK: or anything left over if no ACTION: exists
        talk_matches = TALK_PATTERN.findall(full_response)
        if talk_matches:
            final_talk = " ".join([m.strip() for m in talk_matches if m.strip()])
            # Filter out the action part if it leaked in
            final_talk = re.split(r"ACTION:", final_talk, flags=re.IGNORECASE)[0].strip()
            if final_talk:
                yield {"type": "talk", "content": final_talk}
        elif not action_match:
            # Fallback if AI forgot prefixes but spoke
            yield {"type": "talk", "content": full_response.strip()}

    def execute_task(self, user_request, context=""):
        """Non-streaming wrapper for legacy compatibility."""
        results = list(self.execute_task_stream(user_request, context))
        talk_content = "".join([r['content'] for r in results if r['type'] == 'talk'])
        actions = next((r['actions'] for r in results if r['type'] == 'action'), [])
        
        if actions:
            return {"actions": actions, "reasoning": "Action Path", "assessment": "[SAFE]"}
        return {"actions": [], "message": talk_content, "reasoning": "Conversation Path", "assessment": "[TALK]"}
