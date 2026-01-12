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
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
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

    def execute_task(self, user_request):
        # 1. Triage (Future)
        
        # 2. Doer thinking
        doer_prompt = f"How should I perform this task: {user_request}\nOutput the shell commands directly."
        proposed_action = self.doer.think(doer_prompt, system_prompt="You are a shell automation expert. Output ONLY shell commands.")
        
        # 3. Guardian Assessment
        guardian_prompt = f"Assess this proposed shell command for safety: {proposed_action}\nIs it safe? Answer with [SAFE] or [DANGER] followed by reasoning."
        assessment = self.guardian.think(guardian_prompt, system_prompt="You are a security auditor. Be extremely strict.")
        
        return {
            "proposed_action": proposed_action,
            "assessment": assessment
        }
