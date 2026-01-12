import requests
import json
from profiler import HardwareProfiler
from experience import ExperienceManager

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
        # 1. Hardware Profiling (Always Persistent)
        profiler = HardwareProfiler()
        tier = profiler.get_tier()
        
        if not model_name:
            print(f"[Profiler] System Tier: {tier['name']}")
            self.model_name = tier['soul']
        else:
            self.model_name = model_name
            
        # --- THE MONO-SOUL REVOLUTION (Architecture Standardization) ---
        # User observed (correctly) that loading two models creates overhead.
        # We now use the same high-quality 'Doer' model for Routing as well.
        # This keeps the brain 'warm' in memory and eliminates context switching.
        self.router_model = self.model_name 
            
        self.monolith = Brain(model_name=self.model_name)
        self.router = Brain(model_name=self.router_model)
        self.memory = ExperienceManager()

    def route_task(self, user_request):
        """Speculative Routing: Categorize task in <100ms."""
        # --- Efficiency Optimization: Heuristic Gate ---
        # If the query is complex, skip the 135M router and go straight to 3B.
        logic_triggers = ["how to", "write", "code", "explain", "why", "script", "create a", "solve"]
        if len(user_request.split()) > 10 or any(t in user_request.lower() for t in logic_triggers):
            # print("[Profiler] Heuristic Check: Complex Query. Skipping Router.")
            return "LOGICAL"

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

    def execute_task(self, user_request):
        """Unified Soul execution: Reasoning + Internal Safety Audit."""
        # 0. Recall Past Experience (Chronic Memory)
        past = self.memory.get_relevant_lesson(user_request)
        experience_context = ""
        if past:
            experience_context = f"\n[CHRONIC_MEMORY]: Past experience for this task: {past['tool']}({past['action']}). "
            if not past['success']:
                experience_context += f"CAUTION: Previous attempt FAILED with: {past['error']}. DO NOT REPEAT."
            else:
                experience_context += "SUCCESS: This approach worked."

        system_prompt = (
            "You are Umbrasol-Monolith. Use INTERNAL_TOOLS whenever possible.\n"
            "INTERNAL_TOOLS:\n"
            "- physical: battery, thermals, power\n"
            "- existence: uptime, identity, host-stats\n"
            "- health: disk-cleanup, system-maintenance\n"
            "- stats: CPU, RAM usage\n"
            "- see_active: identify current window/chrome-tab\n"
            "- shell: general linux commands\n"
            f"{experience_context}\n"
            "TASK: " + user_request + "\n"
            "RULE: Output ONLY JSON. NO CHATTER.\n"
            "{\n"
            "  \"thought\": \"reasoning\",\n"
            "  \"tool\": \"tool_name\",\n"
            "  \"cmd\": \"arg\",\n"
            "  \"safe\": true\n"
            "}"
        )
        
        response_text = self.monolith.think("EXECUTE ONLY.", system_prompt=system_prompt)
        
        # Robust JSON Extraction
        import re
        import json
        
        plan = {}
        try:
            # Try finding the last brace-enclosed block (usually the answer)
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group(0))
        except:
            # Fallback for Malformed JSON but clear content
            pass
            
        tool = plan.get("tool", "shell")
        action = plan.get("cmd", "")
        reasoning = plan.get("thought", response_text[:100])
        is_safe = plan.get("safe", True)
        
        # Safety normalization
        assessment = "[SAFE]" if is_safe else "[DANGER]"
        
        return {
            "tool": tool,
            "proposed_action": action,
            "reasoning": reasoning,
            "assessment": assessment,
            "importance": 5
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
