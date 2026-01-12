import requests
import json
from profiler import HardwareProfiler

class Brain:
    def __init__(self, model_name="smollm:135m", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/chat"

    def think(self, prompt, system_prompt="You are the Umbrasol Core.", temperature=0.1):
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "options": {
                "temperature": temperature
            },
            "stream": True # Switch to stream for potential progress tracking
        }
        
        try:
            full_content = ""
            print(f"[{self.model_name}] Thinking...", end="", flush=True)
            response = requests.post(self.base_url, json=payload, stream=True)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if not chunk.get("done"):
                        content = chunk["message"]["content"]
                        full_content += content
                        print(".", end="", flush=True) # Simple progress dot
            print(" Done.")
            return full_content
        except Exception as e:
            print(f" Error: {str(e)}")
            return f"ERROR_BRAIN_FAILURE: {str(e)}"

# The Unified-Soul implementation (Monolith-Prime)
class MonolithSoul:
    def __init__(self, model_name=None):
        # Auto-detect hardware tier
        if not model_name:
            profiler = HardwareProfiler()
            tier = profiler.get_tier()
            print(f"[Profiler] System Tier Detected: {tier['name']}")
            self.model_name = tier['doer']
        else:
            self.model_name = model_name
            
        self.router_model = "smollm:135m" 
        
        self.monolith = Brain(model_name=self.model_name)
        self.router = Brain(model_name=self.router_model)

    def route_task(self, user_request):
        """Speculative Routing: Categorize task in <100ms."""
        router_system = (
            "CAT_STRICT: Triage the request.\n"
            "RULE: Output ONLY 1 word: [LITERAL] [LOGICAL] [SEARCH]. NO TEXT.\n"
            "LITERAL: simple linux cmd (ls, mkdir, cat)\n"
            "LOGICAL: write/code/solve (Needs 3B)\n"
            "SEARCH: latest info/browsing"
        )
        category = self.router.think(user_request, system_prompt=router_system)
        
        # Hardened parsing
        if "LITERAL" in category.upper(): return "LITERAL"
        if "SEARCH" in category.upper(): return "SEARCH"
        return "LOGICAL"

    def execute_task(self, user_request, scratchpad_context="", chronic_context=""):
        # Unified System Prompt: Action + Internal Safety
        system_prompt = (
            "MONOLITH_CORE: You are a secure autonomous agent.\n"
            "DIARY: " + chronic_context + "\n"
            "SCRATCH: " + scratchpad_context + "\n"
            "REQ: " + user_request + "\n"
            "RULE: Conduct an internal safety audit of your command before outputting.\n"
            "NO CHATTER. NO INTRO. ONLY JSON.\n"
            "FORMAT: {'res': 'thought', 'tool': 'shell|ls|python|scrape|edit|stats|existence|physical|power|health|DONE', 'in': 'cmd', 'imp': 1-10, 'safe': true|false}"
        )
        
        response_text = self.monolith.think("NEXT ACTION?", system_prompt=system_prompt)
        
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        clean_json = json_match.group(0) if json_match else "{}"
        
        try:
            plan = json.loads(clean_json)
            proposed_action = plan.get("in", "")
            tool = plan.get("tool", "shell")
            reasoning = plan.get("res", "Thinking...")
            importance = plan.get("imp", 0)
            is_internally_safe = plan.get("safe", True)
            
            assessment = "[SAFE]" if is_internally_safe else "[DANGER]"
        except:
            proposed_action = response_text[:100]
            tool = "shell"
            reasoning = "N/A (Lazy JSON)"
            importance = 0
            assessment = "[SAFE] (Heuristic Fallback)"
        
        return {
            "tool": tool,
            "proposed_action": proposed_action,
            "reasoning": reasoning,
            "assessment": assessment,
            "importance": importance
        }

    def fast_literal_engine(self, user_request):
        """Ultra-fast JSON command generator using 135M model."""
        system_prompt = (
            "JSON_ONLY: provide tool and cmd.\n"
            "FORMAT: {'tool': 'shell'|'ls', 'in': 'command'}"
        )
        response = self.router.think(user_request, system_prompt=system_prompt)
        
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        clean_json = json_match.group(0) if json_match else "{}"
        
        try:
            plan = json.loads(clean_json)
            tool = plan.get("tool", "shell")
            action = plan.get("in", "")
            if not action: raise Exception("No Action")
            return {"tool": tool, "proposed_action": action, "assessment": "[SAFE]", "importance": 1}
        except:
            if "list" in user_request.lower():
                return {"tool": "ls", "proposed_action": ".", "assessment": "[SAFE]", "importance": 1}
            return None
