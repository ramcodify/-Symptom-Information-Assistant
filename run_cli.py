import sys
sys.stdout.reconfigure(encoding="utf-8")

from app.cli import interactive_loop

if __name__ == "__main__":
    interactive_loop()
