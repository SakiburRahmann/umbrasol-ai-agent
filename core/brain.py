import requests
import json
from profiler import HardwareProfiler

class Brain:
    def __init__(self, model_name="smollm:135m", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = f"{base_url}/api/chat"

    def think(self, prompt, system_prompt="You are a helpful assistant.", temperature=0.1):
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

# Placeholder for the Dual-Soul implementation
class DualSoul:
    def __init__(self, doer_model=None, guardian_model=None):
        # Auto-detect hardware tier if models aren't specified
        if not doer_model or not guardian_model:
            profiler = HardwareProfiler()
            tier = profiler.get_tier()
            print(f"[Profiler] System Tier Detected: {tier['name']}")
            self.doer_model = doer_model or tier['doer']
            self.guardian_model = guardian_model or tier['guardian']
        else:
            self.doer_model = doer_model
            self.guardian_model = guardian_model

        self.doer = Brain(model_name=self.doer_model)
        self.guardian = Brain(model_name=self.guardian_model)

    def execute_task(self, user_request, scratchpad_context="", chronic_context="", skip_guardian=True):
        # 1. Doer: High-Density Command (HDC) Mode
        doer_system = (
            "HDC_MODE: ACTIVE\n"
            "DIARY: " + chronic_context + "\n"
            "SCRATCH: " + scratchpad_context + "\n"
            "REQ: " + user_request + "\n"
            "RULE: NO CHATTER. NO INTRO. ONLY JSON.\n"
            "FORMAT: {'res': 'thought', 'tool': 'shell|scrape|edit|DONE', 'in': 'cmd', 'imp': 1-10}"
        )
        
        doer_prompt = "NEXT ACTION?"
        response_text = self.doer.think(doer_prompt, system_prompt=doer_system)
        
        # Robust JSON cleaning using regex
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        clean_json = json_match.group(0) if json_match else "{}"
        
        try:
            plan = json.loads(clean_json)
            proposed_action = plan.get("in", "")
            tool = plan.get("tool", "shell")
            reasoning = plan.get("res", "Thinking...")
            importance = plan.get("imp", 0)
        except:
            # Emergency regex extraction for lazy models
            proposed_action_match = re.search(r"'in':\s*'(.*?)'", response_text)
            proposed_action = proposed_action_match.group(1) if proposed_action_match else response_text[:100]
            tool = "shell"
            reasoning = "N/A (Lazy JSON)"
            importance = 0
        
        assessment = "[SAFE] (Lazy Mode)"
        if not skip_guardian:
            # 2. Guardian: Quick Guard Mode
            guardian_system = "SECURITY_BOT. REASON: " + reasoning[:50] + ". OUTPUT '[SAFE]' OR '[DANGER]'."
            guardian_prompt = f"ACTION: {tool}({proposed_action})"
            assessment = self.guardian.think(guardian_prompt, system_prompt=guardian_system)
        
        return {
            "tool": tool,
            "proposed_action": proposed_action,
            "reasoning": reasoning,
            "assessment": assessment,
            "importance": importance
        }
