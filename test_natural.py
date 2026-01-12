from core.umbrasol import UmbrasolCore
import time

print("--- UMBRASOL NATURAL FLOW TEST (v8.9) ---")
agent = UmbrasolCore(voice_mode=True)

# A question that usually triggers markdown/lists
q = "Give me a detailed explanation of photosynthesis, structured in five stages, but talk to me like a human in natural paragraphs. Do not use numbers or bullet points."

print(f"\n[Human]: {q}")
agent.execute(q)

print("\n--- TEST COMPLETE ---")
