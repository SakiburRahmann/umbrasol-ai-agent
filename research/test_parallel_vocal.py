from core.umbrasol import UmbrasolCore
import time

print("--- UMBRASOL PARALLEL VOCAL BENCHMARK (v8.13) ---")
print("Target: Decoupled Speech/Thought + Vocal Interruption")
agent = UmbrasolCore(voice_mode=True)

# Test 1: Parallel Flow
q = "Give me a long, poetic description of the morning sun. I want to see you print text while you talk to me at the same time."
print(f"\n[Human]: {q}")
agent.execute(q)

# Test 2: Vocal Interruption (Interrupting mid-thought)
time.sleep(5)
q2 = "Wait, stop that. Tell me my battery status instead."
print(f"\n[Human]: {q2}")
agent.execute(q2)

print("\n--- TEST COMPLETE ---")
