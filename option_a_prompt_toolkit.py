"""
Option (a): prompt_toolkit + patch_stdout()
-------------------------------------------
No real network. A fake "receiver" thread pretends to be Minh and
sends a message every few seconds, while you type at any time.

Install:  pip install prompt_toolkit
Run:      python option_a_prompt_toolkit.py
Type /quit to exit.
"""
import random
import threading
import time

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

FAKE_MESSAGES = [
    "Hi Quan, are you there?",
    "Did you finish the slides?",
    "ok, which part?",
    "I will check it again",
    "see you at the demo!",
]

running = True


def fake_receiver(name):
    """Simulates a TCP receiver thread: a message 'arrives' every 3-6 seconds."""
    while running:
        time.sleep(random.uniform(3, 6))
        if running:
            # Inside patch_stdout(), print() is shown ABOVE the input line
            # and the user's half-typed text is redrawn automatically.
            print(f"[{name}] {random.choice(FAKE_MESSAGES)}")


def main():
    global running
    me = "Quan"
    threading.Thread(target=fake_receiver, args=("Minh",), daemon=True).start()

    session = PromptSession()
    print("[*] Connected to Minh (fake). Type messages, /quit to exit.")

    with patch_stdout():
        while True:
            try:
                text = session.prompt("> ")
            except (KeyboardInterrupt, EOFError):
                break
            if text.strip() == "/quit":
                break
            if text.strip():
                print(f"[{me}] {text}")   # in a real app: conn.sendall(...)

    running = False
    print("[*] Bye!")


if __name__ == "__main__":
    main()
