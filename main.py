import sys
import os
import asyncio

# Ensure we can import from core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.umbrasol import UmbrasolCore

async def main():
    voice_mode = "--voice" in sys.argv
    agent = UmbrasolCore(voice_mode=voice_mode)
    await agent.initialize()
    
    if voice_mode:
        await agent.listen_loop()
    elif len(sys.argv) > 1:
        # Reconstruct command excluding flags
        command = " ".join([arg for arg in sys.argv[1:] if not arg.startswith("--")])
        if command:
            result = await agent.execute(command)
            if result:
                print(f"\n[Umbrasol]: {result}")
        else:
            print("No command provided. Use Umbrasol with --voice or 'your command'.")
    else:
        print("\nUsage:")
        print("  python main.py --voice         # Hands-free mode")
        print("  python main.py \"command\"       # Single execution")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
