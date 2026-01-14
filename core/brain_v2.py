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
        """Stream decision using THINK/SAY/ACT (Ultra-Resilient Protocol)."""
        system_name = getattr(settings, "SYSTEM_NAME", "Umbrasol")
        identity = f"Identity: {system_name} (Operator). Rule: Output ONLY THINK: and ACT:. No talking."
        tool_desc = "net: search; stats: system; see_active: window; ls: files."

        prompt = (
            f"Context: {context}\nInput: {user_request}\n"
            f"Tools: {tool_desc}\n\n"
            "Example:\nTHINK: User wants to know time.\nACT: shell,date\n\n"
            "Format:\nTHINK: [Logic]\nACT: tool,query"
        )

        full_response = ""
        last_emitted_pos = 0
        current_type = None

        async for chunk in self.monolith.think_stream(prompt, system_prompt=identity, temperature=0.1, max_tokens=600):
            full_response += chunk
            
            lines = full_response.splitlines()
            if not lines: continue
            last_line = lines[-1].strip()
            
            if last_line.startswith("THINK:") and current_type != "reasoning":
                current_type = "reasoning"
                last_emitted_pos = full_response.rfind("THINK:") + 6
            elif last_line.startswith("SAY:") and current_type != "talk":
                current_type = "talk"
                last_emitted_pos = full_response.rfind("SAY:") + 4
            elif last_line.startswith("ACT:") and current_type != "action":
                current_type = "action"
                last_emitted_pos = full_response.rfind("ACT:")
                break

            if current_type in ["talk", "reasoning"]:
                content_chunk = full_response[last_emitted_pos:]
                if not any(f"\n{p}:" in content_chunk for p in ["SAY", "ACT", "THINK"]):
                    if content_chunk:
                        yield {"type": current_type, "content": content_chunk}
                        last_emitted_pos = len(full_response)

        # ROBUST ACT PARSING
        import re
        # Look for ACT: or holistic scan for keywords if ACT: is missing
        ACT_PATTERN = re.compile(r"ACT:?\s*(.*)", re.IGNORECASE)
        actions = []
        
        TOOL_MAP = {
            "net": ["net", "search", "web", "internet", "google", "ddg", "search for", "online", "price of"],
            "stats": ["stats", "load", "ram", "cpu", "system", "vitals", "memory"],
            "ls": ["ls", "list", "files", "dir"],
            "shell": ["shell", "terminal", "bash", "cmd"],
            "see_active": ["active", "window"]
        }

        # First pass: Look for explicit ACT: tags
        found_explicit = False
        for match in ACT_PATTERN.finditer(full_response):
            raw = match.group(1).strip().split("SAY:")[0].split("\n")[0]
            if not raw or len(raw) < 2: continue # Ignore noise
            found_explicit = True
            self._add_action(actions, raw, TOOL_MAP)

        # Second pass: If NO explicit actions found, scan the REASONING chunks for intent
        if not found_explicit:
            detected_intents = []
            for tool_name, kws in TOOL_MAP.items():
                if any(kw in full_response.lower() for kw in kws):
                    detected_intents.append(tool_name)
            
            for tool_name in detected_intents:
                # Use the user request as base
                query = user_request
                
                # CROSS-TOOL STRIPPING: Remove mentions of OTHER tools to focus this query
                for other_tool, other_kws in TOOL_MAP.items():
                    if other_tool == tool_name: continue
                    for okw in other_kws:
                        # Remove "and check RAM", "list files in core", etc.
                        query = re.sub(rf"(?:and|also|then|finally|,)?\s*(?:check|run|use|list|search|tell me)?\s*\b{re.escape(okw)}\b.*?(?:and|also|then|finally|,|$)", "", query, flags=re.IGNORECASE).strip()
                
                # TOOL-SPECIFIC HARDENING
                if tool_name == "ls":
                    # If looking for a directory, try to isolate it
                    match = re.search(r"(?:in|of)\s+['\"]?([\w/.-]+)['\"]?", query)
                    if match: query = match.group(1)
                elif tool_name == "net":
                    # Strip common net prefixes
                    query = re.sub(r"^(search|check|find|tell me|what is|how is)\s+(?:for|about|the)?\s*", "", query, flags=re.IGNORECASE)
                
                actions.append({"tool": tool_name, "cmd": query})

        if actions:
            yield {"type": "action", "actions": actions}

    def _add_action(self, actions, raw, tool_map):
        import re
        found_t = None
        for tool_name, kws in tool_map.items():
            if any(k in raw.lower() for k in kws):
                found_t = tool_name
                break
        
        if not found_t: found_t = "stats"
        
        if "," in raw:
            query = raw.split(",", 1)[1].strip()
        else:
            query = raw
            search_space = tool_map.get(found_t, []) + [found_t]
            for kw in sorted(search_space, key=len, reverse=True):
                if kw.lower() in query.lower():
                    query = re.sub(rf".*?\b{re.escape(kw)}\b[:\s]*", "", query, count=1, flags=re.IGNORECASE)
                    break
        
        # ADVANCED QUERY STRIPPING
        query = query.strip().strip('"').strip("'").strip("()").strip("[]")
        # Strip prepositional phrases and filler
        fillers = [
            r"^(in|for|using|searching|querying|about|the|a)\s+",
            r"^the\s+files?\s+in\s+the\s+",
            r"^the\s+directory\s+",
            r"\s+directory\.?$",
            r"\s+folder\.?$"
        ]
        for f in fillers:
            query = re.sub(f, "", query, flags=re.IGNORECASE).strip()
            
        if query:
            actions.append({"tool": found_t, "cmd": query})

    async def synthesis_stream(self, user_request, tool_results):
        """Pure conversational synthesis."""
        system_name = getattr(settings, "SYSTEM_NAME", "Umbrasol")
        identity = f"Identity: {system_name}, Synthesizer."
        prompt = f"User: {user_request}\nResults: {tool_results}\n\nSAY: [Your summary]"

        async for chunk in self.monolith.think_stream(prompt, system_prompt=identity, temperature=0.3, max_tokens=500):
            yield {"type": "talk", "content": chunk.replace("SAY:", "").strip()}

    async def execute_task(self, user_request, context=""):
        """Non-streaming wrapper."""
        results = []
        async for res in self.execute_task_stream(user_request, context):
            results.append(res)
        return results
