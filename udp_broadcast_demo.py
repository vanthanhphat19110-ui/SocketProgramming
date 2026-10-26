"""
UDP broadcast demo: 3 instances on ONE machine share UDP port 9999.

Open 3 terminals:
    python udp_broadcast_demo.py listen --name B
    python udp_broadcast_demo.py listen --name C
    python udp_broadcast_demo.py send   --name A

A broadcasts "HELLO|A|5001|online" every 3 s; B and C both receive it.
If you have no network (offline laptop), add:  --bcast 127.255.255.255
"""
import argparse
import socket
import time

PORT = 9999


def make_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow several processes to bind the same UDP port (must be BEFORE bind)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):          # needed on macOS/BSD
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(("", PORT))                           # "" = all interfaces
    return s


def listen(name):
    s = make_socket()
    print(f"[{name}] listening on UDP {PORT} ...")
    while True:
        data, addr = s.recvfrom(1024)
        msg = data.decode("utf-8", errors="replace")
        parts = msg.split("|")
        if len(parts) == 4 and parts[0] == "HELLO" and parts[1] == name:
            continue                             # ignore my own broadcast
        print(f"[{name}] got {msg!r} from {addr[0]}:{addr[1]}")


def send(name, bcast, tcp_port):
    s = make_socket()
    msg = f"HELLO|{name}|{tcp_port}|online".encode()
    print(f"[{name}] broadcasting to {bcast}:{PORT} every 3 s (Ctrl+C to stop)")
    while True:
        s.sendto(msg, (bcast, PORT))
        print(f"[{name}] sent {msg.decode()}")
        time.sleep(3)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("role", choices=["listen", "send"])
    p.add_argument("--name", required=True)
    p.add_argument("--bcast", default="255.255.255.255")
    p.add_argument("--tcp-port", type=int, default=5001)
    a = p.parse_args()
    try:
        listen(a.name) if a.role == "listen" else send(a.name, a.bcast, a.tcp_port)
    except KeyboardInterrupt:
        print("\nbye")
