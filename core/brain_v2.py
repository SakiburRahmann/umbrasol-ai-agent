import requests
import json
from core.profiler import HardwareProfiler
from core.experience import ExperienceManager
from config import settings
import os

class Brain:
    def __init__(self, model_name="qwen2.5:3b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/generate"

    def think_stream(self, prompt, system_prompt="", temperature=0.7, max_tokens=150, timeout=60):
        """Streaming inference for real-time response with timeout protection."""
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n{prompt}",
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_thread": os.cpu_count() or 4,  # Use CPU count, fallback to 4
                "num_ctx": 4096
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=timeout, stream=True)
            response.raise_for_status()
            
            import time
            start_time = time.time()
            last_chunk_time = start_time
            chunk_timeout = 30  # Max time between chunks
            
            for line in response.iter_lines():
                current_time = time.time()
                
                # Check for overall timeout
                if current_time - start_time > timeout:
                    yield f"ERROR: Streaming timeout after {timeout}s"
                    break
                
                # Check for chunk timeout (no data received)
                if current_time - last_chunk_time > chunk_timeout:
                    yield f"ERROR: No data received for {chunk_timeout}s"
                    break
                
                if line:
                    last_chunk_time = current_time
                    chunk = json.loads(line)
                    if chunk.get("done", False):
                        break
                    yield chunk.get("response", "")
        except requests.exceptions.Timeout:
            yield f"ERROR: Connection timeout to Ollama"
        except requests.exceptions.ConnectionError:
            yield f"ERROR: Cannot connect to Ollama. Is it running?"
        except requests.exceptions.RequestException as e:
            yield f"ERROR: Request failed: {str(e)}"
        except Exception as e:
            yield f"ERROR: {str(e)}"

class MonolithSoul:
    def __init__(self, override_model=None):
        """Initialize with optional model override for testing."""
        profiler = HardwareProfiler()
        tier = profiler.get_tier()
        # Allow overriding for testing different models
        self.model_name = override_model or tier['soul']
        self.monolith = Brain(model_name=self.model_name)
        self.memory = ExperienceManager()
        self.safe_tools = settings.SAFE_TOOLS

    def execute_task_stream(self, user_request, context=""):
        """Stream decision and response for real-time interaction."""
        system_name = getattr(settings, "SYSTEM_NAME", "Umbrasol")
        
        identity = (
            f"You are {system_name}, an autonomous local AI agent. "
            "You are witty, helpful, and strictly follow the protocol below."
        )
        
        # Tool hints for AI reasoning
        tool_hints = "stats: system load; see_active: window name; proc_list: tasks; ls: files; shell: commands"
        
        prompt = (
            f"Context: {context}\n"
            f"User: {user_request}\n\n"
            f"Tools: {tool_hints}\n"
            "Format Rules:\n"
            "1. ALWAYS prefix talk with 'TALK: '. Be creative and articulate.\n"
            "2. ALWAYS prefix actions with 'ACTION: tool,cmd'. Example: 'ACTION: stats,'\n"
            "3. You MUST provide BOTH if requested. Talk first, then Action."
        )
        
        import re
        full_response = ""
        last_yield_pos = 0
        
        # Action/Talk state tracking
        in_action = False
        
        for chunk in self.monolith.think_stream(prompt, system_prompt=identity, temperature=0.7, max_tokens=300):
            full_response += chunk
            
            # Streaming Logic (State-based)
            # Find the most recent prefix
            talk_idx = full_response.rfind("TALK:")
            action_idx = full_response.rfind("ACTION:")
            
            if talk_idx > action_idx:
                # We are in a talk segment
                talk_content = full_response[talk_idx + 5:]
                # Yield new text excluding any Action prefixes if they leaked
                if "ACTION:" not in talk_content:
                    new_text = talk_content[last_yield_pos:]
                    if new_text:
                        yield {"type": "talk", "content": new_text}
                        last_yield_pos = len(talk_content)
            elif action_idx > talk_idx:
                # We reached an action segment, stop yielding talk
                pass

        # FINAL ROBUST PARSING
        # Regex Patterns
        ACTION_PATTERN = re.compile(r"ACTION:\s*([^,\n]*),\s*(.*)", re.IGNORECASE)
        
        for match in ACTION_PATTERN.finditer(full_response):
            tool = match.group(1).strip().lower()
            cmd = match.group(2).strip()
            
            # Fuzzy match tool
            if tool not in self.safe_tools:
                for t in self.safe_tools:
                    if tool in t or t in tool:
                        tool = t
                        break
                else: tool = "stats"
            
            # Clean cmd of potential trailing Talk or protocol leaks
            cmd = re.split(r"TALK:", cmd, flags=re.IGNORECASE)[0].strip()
            cmd = cmd.split("ACTION:")[0].split("Tools:")[0].split("Format:")[0].strip()
            if any(p in cmd.lower() for p in settings.SENSITIVE_PATTERNS): cmd = ""
            
            yield {
                "type": "action",
                "actions": [{"tool": tool, "cmd": cmd}],
                "reasoning": "Standard Action Path"
            }
        
        # Fallback if no prefixes used at all
        if "TALK:" not in full_response and "ACTION:" not in full_response:
            yield {"type": "talk", "content": full_response.strip()}

    def execute_task(self, user_request, context=""):
        """Non-streaming wrapper for legacy compatibility."""
        results = list(self.execute_task_stream(user_request, context))
        talk_content = "".join([r['content'] for r in results if r['type'] == 'talk'])
        actions = next((r['actions'] for r in results if r['type'] == 'action'), [])
        
        if actions:
            return {"actions": actions, "reasoning": "Action Path", "assessment": "[SAFE]"}
        return {"actions": [], "message": talk_content, "reasoning": "Conversation Path", "assessment": "[TALK]"}
