"""
Option (b): read keys one at a time + manual redraw (bonus version)
-------------------------------------------------------------------
No real network. A fake "receiver" thread pretends to be Minh and
sends a message every few seconds, while you type at any time.

No extra libraries needed.
Run:   python option_b_manual_redraw.py
Type /quit to exit.

How it works:
  - The main thread reads ONE key at a time and keeps the typed text in `buffer`.
  - When a message arrives, the receiver thread:
        1. erases the input line      ("\r" + "\033[K")
        2. prints the message + newline
        3. redraws "> " + buffer      (so the half-typed text is not lost)
  - `screen_lock` makes sure only one thread writes to the screen at a time.
"""
import os
import random
import sys
import threading
import time

# ---------------------------------------------------------------------------
# Read a single key without waiting for Enter (Windows + Linux/macOS)
# ---------------------------------------------------------------------------
if os.name == "nt":
    import msvcrt

    os.system("")  # enables ANSI escape codes (\033[K) in the Windows console

    def get_key():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):     # arrow / function keys send 2 codes
            msvcrt.getwch()            # read and ignore the second code
            return None
        return ch

    def setup_terminal():
        return None

    def restore_terminal(_):
        pass
else:
    import termios
    import tty

    def get_key():
        ch = sys.stdin.read(1)
        if ch == "\x1b":               # arrow keys: ESC [ A  -> ignore
            sys.stdin.read(2)
            return None
        return ch

    def setup_terminal():
        old = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())   # keys arrive one by one, no echo
        return old

    def restore_terminal(old):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)


# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------
PROMPT = "> "
CLEAR_LINE = "\r\033[K"        # go to start of line + erase to end of line

buffer = ""                    # text the user has typed so far
screen_lock = threading.Lock()
running = True


def show_message(line):
    """Print a line ABOVE the input line, then redraw prompt + typed text.
    Called by any thread (receiver, file sender, UDP listener, ...)."""
    with screen_lock:
        sys.stdout.write(CLEAR_LINE)          # 1. erase input line
        sys.stdout.write(line + "\n")         # 2. print the message
        sys.stdout.write(PROMPT + buffer)     # 3. redraw prompt + typed text
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Fake receiver thread (replaces the real TCP recv() loop)
# ---------------------------------------------------------------------------
FAKE_MESSAGES = [
    "Hi Quan, are you there?",
    "Did you finish the slides?",
    "ok, which part?",
    "I will check it again",
    "see you at the demo!",
]


def fake_receiver(name):
    while running:
        time.sleep(random.uniform(3, 6))
        if running:
            # Real app: data = conn.recv(4096); show_message(f"[{name}] {data.decode()}")
            show_message(f"[{name}] {random.choice(FAKE_MESSAGES)}")


# ---------------------------------------------------------------------------
# Main thread: keyboard loop
# ---------------------------------------------------------------------------
def main():
    global buffer, running
    me = "Quan"

    print("[*] Connected to Minh (fake). Type messages, /quit to exit.")
    old_settings = setup_terminal()
    threading.Thread(target=fake_receiver, args=("Minh",), daemon=True).start()

    sys.stdout.write(PROMPT)
    sys.stdout.flush()

    try:
        while True:
            ch = get_key()
            if ch is None:
                continue

            with screen_lock:
                if ch in ("\r", "\n"):                      # Enter -> send
                    text = buffer
                    buffer = ""
                    if text.strip() == "/quit":
                        sys.stdout.write("\n")
                        break
                    sys.stdout.write(CLEAR_LINE)
                    if text.strip():
                        sys.stdout.write(f"[{me}] {text}\n")
                        # Real app: conn.sendall(text.encode())
                    sys.stdout.write(PROMPT)

                elif ch in ("\b", "\x7f"):                  # Backspace
                    if buffer:
                        buffer = buffer[:-1]
                        sys.stdout.write("\b \b")           # move back, erase, move back

                elif ch == "\x03":                          # Ctrl+C
                    sys.stdout.write("\n")
                    break

                elif ch.isprintable():                      # normal character
                    buffer += ch
                    sys.stdout.write(ch)

                sys.stdout.flush()
    finally:
        running = False
        restore_terminal(old_settings)
        print("[*] Bye!")


if __name__ == "__main__":
    main()
