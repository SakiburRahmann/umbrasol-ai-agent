import sys
import os

# Ensure we can import from core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.umbrasol import UmbrasolCore
except ImportError as e:
    print(f"CRITICAL ERROR: Could not import Umbrasol Core. {e}")
    sys.exit(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--voice":
        # Voice Mode
        agent = UmbrasolCore(voice_mode=True)
        agent.listen_loop()
    elif len(sys.argv) > 1:
        # CLI Command Mode (Voice mode False by default)
        agent = UmbrasolCore(voice_mode=False)
        command = " ".join(sys.argv[1:])
        result = agent.execute(command)
        if result:
            print(f"\n[Umbrasol]: {result}")
    else:
        # Help / Interactive (Future)
        print("\nUsage:")
        print("  python main.py --voice         # Hands-free mode")
        print("  python main.py \"command\"       # Single execution")
        print("  python main.py check battery   # Example")

if __name__ == "__main__":
    main()
