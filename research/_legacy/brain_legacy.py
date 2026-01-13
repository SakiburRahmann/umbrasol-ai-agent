import requests
import json
from profiler import HardwareProfiler
from experience import ExperienceManager

class Brain:
    def __init__(self, model_name="smollm:135m", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/chat"

    def think(self, prompt, system_prompt="You are the Umbrasol Core.", temperature=0.0, stream=False):
        # Performance Optimizations for Local Hardware
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "options": {
                "temperature": temperature,
                "num_thread": 8, # Force multi-core usage
                "num_ctx": 2048,  # Keep context small for speed
                "repeat_penalty": 1.2
            },
            "stream": True
        }
        
        try:
            full_content = ""
            if not stream:
                print(f"[{self.model_name}] Thinking...", end="", flush=True)
            
            response = requests.post(self.base_url, json=payload, stream=True)
            response.raise_for_status()
            
            def generator():
                nonlocal full_content
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if not chunk.get("done"):
                            content = chunk["message"]["content"]
                            full_content += content
                            yield content

            if stream:
                return generator()
            else:
                for content in generator():
                    print(".", end="", flush=True)
                print(" Done.")
                return full_content
        except Exception as e:
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

    def execute_task(self, user_request, callback=None):
        """Action-First Execution: Get the tool, then think."""
        past = self.memory.get_relevant_lesson(user_request)
        xp = f"XP: {past['tool']}({past['action']})=FAIL" if past and not past['success'] else ""

        system_prompt = (
            "JSON-FIRST. NO TEXT. "
            "{\"tool\": \"..\", \"cmd\": \"..\", \"thought\": \"..\"}\n"
            "TOOLS: physical(bat|temp), existence(up|id), stats(cpu|ram), see(act|tree|raw), gui(click|type|scroll|speak), shell(cmd).\n"
            f"{xp}"
        )
        
        # Performance payload with 4 threads
        response_gen = self.monolith.think(user_request, system_prompt=system_prompt, stream=True)
        
        response_text = ""
        plans = []
        
        print(f"[{self.model_name}] Velocity-Pulse... ", end="", flush=True)
        for chunk in response_gen:
            response_text += chunk
            
            # EAGER PARSING: Look for the FIRST closed JSON block
            if "}" in response_text:
                try:
                    json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
                    if json_match:
                        plan = json.loads(json_match.group(0))
                        if "tool" in plan and "cmd" in plan:
                            if plan not in plans:
                                plans.append(plan)
                                if callback: callback(plan) # EXECUTE NOW
                                print("⚡", end="", flush=True)
                                # If it's the first action, we can potentially keep going or stop
                except: pass
            
            # Velocity Stop: If we have an action and it starts chatting
            if len(plans) > 0 and len(response_text) > (len(json.dumps(plans[0])) + 20):
                break

        return {"actions": plans, "reasoning": response_text[:50]}

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
