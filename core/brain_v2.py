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

        last_yield_pos = 0
        
        for chunk in self.monolith.think_stream(prompt, system_prompt=identity):
            # print(f"DEBUG BRAIN: {chunk}")
            full_response += chunk
            
            # Simple Streaming (bypass regex for raw speed debug)
            # Just yield new chars if they look like part of a Talk segment
            if len(full_response) > last_yield_pos:
                new_text = full_response[last_yield_pos:]
                # Stripping styling artifacts if any
                if "TALK:" not in new_text and "ACTION:" not in new_text:
                     yield {"type": "talk", "content": new_text}
                     last_yield_pos = len(full_response)

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
