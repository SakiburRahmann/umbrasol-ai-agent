import sys
import os
import time
import asyncio
import logging
import atexit
import signal
from concurrent.futures import ThreadPoolExecutor

from core.tools import OperatorInterface
from core.brain_v2 import MonolithSoul
from core.cache import SemanticCache
from core.habit import HabitManager
from core.omega_memory import OmegaMemory
from core.omega_safety import OmegaSafety
from core.internet import Internet
import re
from config import settings

# Configure Logging
logging.basicConfig(
    filename=os.path.join(settings.LOG_DIR, "umbrasol.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class UmbrasolCore:
    """
    Umbrasol v12.0: The Renaissance Soul (Async & JSON)
    High-performance async orchestrator.
    """
    def __init__(self, voice_mode=False):
        self.logger = logging.getLogger("Core")
        self.voice_mode = voice_mode
        self.soul = MonolithSoul()
        self.hands = OperatorInterface()
        self.memory = OmegaMemory()
        self.cache = SemanticCache(memory=self.memory)
        self.habit = HabitManager(memory=self.memory)
        self.safety = OmegaSafety()
        self.net = Internet()
        
        # Ensure directories exist
        os.makedirs(settings.LOG_DIR, exist_ok=True)
        
        # Phase 10: RESILIENCE
        self.lock_file = os.path.join(settings.LOG_DIR, "core.lock")
        self._detect_crash()
        with open(self.lock_file, "w") as f:
            f.write(str(os.getpid()))
        
        # Register cleanup handlers (sync for atexit)
        atexit.register(self._cleanup_sync)
        
        # Identity
        print(f"--- {settings.SYSTEM_NAME} {settings.VERSION} ---")
        self.logger.info(f"System ONLINE (ASYNC) | Safety: GUARDIAN")

    def _detect_crash(self):
        if os.path.exists(self.lock_file):
            print("[ALARM] Abnormal termination detected. Cleaning up lock...")
            self.logger.warning("Crash detected on startup.")
            os.remove(self.lock_file)

    def _cleanup_sync(self):
        """Sync cleanup for atexit."""
        if hasattr(self, 'lock_file') and os.path.exists(self.lock_file):
            os.remove(self.lock_file)

    async def initialize(self):
        """Async initialization for SQLite and other components."""
        await self.memory.ensure_db()
        
        # Register signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))
        
        # HEALTH MONITOR
        asyncio.create_task(self._health_monitor())
        
        # RESUME PATH
        await self._handle_task_resume()
        
        if self.voice_mode:
            await self._safe_dispatch("gui_speak", "System online. I am evolving.")

    async def shutdown(self):
        self.logger.info("Graceful shutdown initiated...")
        if hasattr(self, 'memory'):
            await self.memory.close()
        self._cleanup_sync()
        sys.exit(0)

    async def _health_monitor(self):
        while True:
            await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
            self.logger.debug("Health Check: ACTIVE")

    async def _handle_task_resume(self):
        pending = await self.memory.get_pending_tasks()
        if pending:
            max_resume = min(len(pending), settings.MAX_TASK_RESUME)
            pending = pending[:max_resume]
            print(f"[RECOVERY] Resuming {len(pending)} tasks...")
            
            for task in pending:
                asyncio.create_task(self.execute(task['request'], task_id=task['id']))

    async def execute(self, user_request: str, task_id: str | None = None) -> str | None:
        start_time = time.time()
        
        if not task_id:
            task_id = await self.memory.add_task(user_request)
        
        print(f"\n[Request]: {user_request}")
        self.logger.info(f"Task {task_id} Initiated")

        # LAYER 1: CONTEXT SENSING
        active_window = await self._safe_dispatch("see_active", "")
        context_str = f"[Active Window: {active_window}]"
        
        # LAYER 2: INTERRUPT PREVIOUS
        await self._safe_dispatch("stop_speaking", "")

        # LAYER 3: SEMANTIC CACHE
        cached = await self.cache.get(user_request)
        if cached:
            print(f"[CACHE] Hit!")
            result = await self._safe_dispatch(cached['tool'], cached['command'])
            await self._log_result(result, start_time, task_id, cached['tool'], cached['command'])
            await self.memory.update_task_checkpoint(task_id, "completed", {"stage": "cache_hit"})
            return str(result)

        # LAYER 4: INSTANT HEURISTICS
        req = user_request.lower().strip()
        word_count = len(req.split())
        instant_map = getattr(settings, "INSTANT_MAP", {})
        
        if word_count < settings.HEURISTIC_WORD_THRESHOLD:
            for key, (tool, cmd) in instant_map.items():
                if key in req:
                    print(f"[INSTANT] Matched: {tool}")
                    result = await self._safe_dispatch(tool, cmd)
                    await self._log_result(result, start_time, task_id, tool, cmd)
                    await self.memory.update_task_checkpoint(task_id, "completed", {"stage": "heuristic"})
                    return str(result)

        # LAYER 5: AI BRAIN
        print(f"[AI] Thinking...")
        await self.memory.update_task_checkpoint(task_id, "running", {"stage": "thinking"})
        
        full_message = ""
        actions = []
        
        print(f"[AI] ", end="", flush=True)
        async for chunk_data in self.soul.execute_task_stream(user_request, context=context_str):
            if chunk_data["type"] == "talk":
                content = chunk_data["content"]
                # Filter out raw SAY: or THINK: leftovers if they slip through
                content = re.sub(r"^(SAY|THINK|ACT):?\s*", "", content, flags=re.IGNORECASE)
                full_message += content
                sys.stdout.write(content)
                sys.stdout.flush()
                if self.voice_mode:
                    await self._safe_dispatch("gui_speak", content.strip())
            
            elif chunk_data["type"] == "reasoning":
                content = chunk_data["content"].strip()
                if content:
                    if "[Thinking]:" not in full_message:
                        sys.stdout.write(f"\n[Thinking]: ")
                        full_message += "[Thinking]: "
                    sys.stdout.write(f"{content} ")
                    sys.stdout.flush()
            
            elif chunk_data["type"] == "action":
                actions.extend(chunk_data.get("actions", []))
        print("\n") # End the AI response line


        # EXECUTION PATH
        success = True
        last_result = None
        
        for action in actions:
            tool = action.get("tool", "stats")
            cmd = action.get("cmd", "")
            
            # Safety Guards
            risk = self.safety.analyze_risk(f"{tool} {cmd}")
            if risk != "LOW":
                print(f"[SAFETY] {risk} Risk Detected!")
                if risk in ["MEDIUM", "HIGH"]:
                    self.safety.snapshot(cmd) # Sync snapshot is okay here

            # Self-Correction Loop
            action_success = False
            for attempt in range(settings.MAX_RETRIES + 1):
                await self.memory.update_task_checkpoint(task_id, "running", {"stage": "executing", "tool": tool, "cmd": cmd})
                
                result = await self._safe_dispatch(tool, cmd)
                last_result = result
                res_str = str(result)
                print(f"[Result]: {res_str[:200]}")
               
                if "ERROR" not in res_str and "BLOCKED" not in res_str:
                    action_success = True
                    break
                
                if attempt < settings.MAX_RETRIES:
                    print(f"[AUTO-FIX] Retrying...")
                    await asyncio.sleep(1) # Simple backoff
            
            if not action_success:
                success = False
                break
        
        # SYNTHESIS PASS: If tools were used, inform the AI of the result to provide a final summary
        if actions and success:
            print(f"[AI] Synthesizing results...")
            async for chunk_data in self.soul.synthesis_stream(user_request, last_result):
                if chunk_data["type"] == "talk":
                    content = chunk_data["content"]
                    full_message += content
                    sys.stdout.write(content)
                    sys.stdout.flush()

        
        # Patterns & Learning
        if success and len(actions) == 1:
            await self.cache.set(user_request, actions[0]['tool'], actions[0]['cmd'])
            await self.habit.learn(active_window, f"{actions[0]['tool']}:{actions[0]['cmd']}")

        await self.memory.update_task_checkpoint(task_id, "completed" if success else "failed", {"stage": "finished"})
        print(f"[Time]: {time.time() - start_time:.3f}s")
        
        return full_message if full_message else str(last_result) if last_result else None

    async def _safe_dispatch(self, tool, cmd):
        """Unified dispatch to tools.py, handling both sync and async."""
        try:
            # Dispatch mapping
            dispatch = {
                "physical": self.hands.get_physical_state,
                "existence": self.hands.get_existence_stats,
                "stats": self.hands.get_system_stats,
                "see_active": self.hands.read_active_window,
                "see_raw": self.hands.ocr_screen,
                "proc_list": self.hands.get_process_list,
                "power": lambda: self.hands.power_control(cmd),
                "shell": lambda: self.hands.execute_shell(cmd),
                "gui_speak": lambda: self.hands.gui_speak(cmd),
                "stop_speaking": self.hands.stop_speaking,
                "ls": lambda: self.hands.list_dir(cmd or "."),
                "net": lambda: self.net.swift_search(cmd),
            }
            
            if tool in dispatch:
                func = dispatch[tool]
                if asyncio.iscoroutinefunction(func):
                    return await func()
                elif callable(func):
                    # Run potentially blocking sync calls in a thread pool to keep the loop free
                    return await asyncio.to_thread(func)
                else:
                    return func
            return f"BLOCKED: Tool '{tool}' not found"
        except Exception as e:
            self.logger.error(f"Dispatch Error: {e}")
            return f"ERROR: {e}"

    async def _log_result(self, result, start_time, task_id, tool, cmd):
        risk = self.safety.analyze_risk(f"{tool} {cmd}")
        await self.memory.log_action(f"{tool}({cmd})", str(result), risk)

    async def listen_loop(self):
        """Async version of the voice listener loop."""
        from core.ear import Ear
        ear = Ear()
        if not ear.model: return

        print("[VOICE] Listening (Async)...")
        self.voice_mode = True 
        
        while True:
            # We use to_thread for ear.listen_once because VOSK is blocking
            command = await asyncio.to_thread(ear.listen_once)
            if command:
                print(f"\n[VOICE] Heard: '{command}'")
                await self.execute(command)

async def main_async():
    agent = UmbrasolCore(voice_mode="--voice" in sys.argv)
    await agent.initialize()
    
    if "--voice" in sys.argv:
        await agent.listen_loop()
    elif len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        await agent.execute(command)
    else:
        print("Usage: python core/umbrasol.py 'command' OR --voice")

if __name__ == "__main__":
    asyncio.run(main_async())
