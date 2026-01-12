from core.umbrasol import UmbrasolCore
import time

print("--- UMBRASOL v8.0 DUAL-PATH VALIDATION (Fixed) ---")
agent = UmbrasolCore(voice_mode=True)

# Test 1: System Level
print("\n[Human]: Give me my system stats.")
agent.execute("Give me my system stats.")
time.sleep(5)

# Test 2: Conversational Level
print("\n[Human]: If you were a real person, what would be your favorite thing to learn about?")
agent.execute("If you were a real person, what would be your favorite thing to learn about?")
time.sleep(15)

# Test 3: Hybrid
print("\n[Human]: List the files and tell me what you think of our project's architecture.")
agent.execute("List the files and tell me what you think of our project's architecture.")

print("\n--- FINAL VALIDATION COMPLETE ---")
