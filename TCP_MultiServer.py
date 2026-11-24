import socket
from threading import Thread

HOST, PORT = "127.0.0.1", 5000

def handle_client(connection, address):
    print(f"[+] {address} connected.")
    with connection:
        while True:
            data = connection.recv(1024)
            if (not data or data == b"bye"): break # client left the chat.

            message = data.decode() # sockets carry bytes, not text --> encode before sending, decode after receiving.
            print(f"[{address[1]}] {message}")

            reply = f"Server got: {message}"
            connection.sendall(reply.encode()) # The multiserver replies automatically, so no keyboard input is needed.
    print(f"[-] {address} disconnected.")

if __name__ == "__main__":
    multiserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    multiserver.bind((HOST, PORT))
    multiserver.listen(5) # multiserver listens to 05 clients (max).
    print(f"Server is listenning on port {PORT}.")
    print(f"Waiting for clients ...")

    while True:
        connection, address = multiserver.accept() # main thread: accept only.
        t = Thread(target = handle_client, args = (connection, address))
        t.daemon = True
        t.start()