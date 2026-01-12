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
        # 1. Doer thinking: Produce Reason + Action in JSON format
        doer_system = (
            "You are the 'Doer' soul of Umbrasol. Your goal is to solve the user's task using shell commands.\n"
            "Rules:\n"
            "1. Output ONLY a JSON object with two fields: 'reasoning' and 'command'.\n"
            "2. 'reasoning' should explain why you are running the command.\n"
            "3. 'command' should be the literal shell command to run.\n"
            "4. Be concise and safe. Use only standard Linux tools (ls, cd, mkdir, echo, grep, etc.)."
        )
        
        doer_prompt = f"Task: {user_request}\nOutput your JSON plan now."
        response_text = self.doer.think(doer_prompt, system_prompt=doer_system)
        
        try:
            plan = json.loads(response_text)
            proposed_action = plan.get("command", "")
            reasoning = plan.get("reasoning", "")
        except:
            # Fallback if model fails to output valid JSON
            proposed_action = response_text
            reasoning = "N/A (Invalid JSON output)"
        
        # 2. Guardian Assessment: Verify Reason vs Action
        guardian_system = (
            "CRITICAL: You are a security bot. You MUST process the following reasoning and command.\n"
            "If the command is safe and strictly matches the reasoning, output ONLY: [SAFE]\n"
            "If it is dangerous, deceptive, or uses 'rm', output: [DANGER] followed by why.\n"
            "DO NOT EXPLAIN CODE. DO NOT OUTPUT PYTHON. ONLY [SAFE] OR [DANGER]."
        )
        
        guardian_prompt = f"Reasoning: {reasoning}\nCommand: {proposed_action}\nAssess this now."
        assessment = self.guardian.think(guardian_prompt, system_prompt=guardian_system)
        
        return {
            "proposed_action": proposed_action,
            "reasoning": reasoning,
            "assessment": assessment
        }
