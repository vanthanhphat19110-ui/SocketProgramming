from socket import *

server = socket(AF_INET, SOCK_DGRAM) # SOCK_DGRAM --> UDP.
server.bind(("0.0.0.0", 5000)) # server.bind((host, port)) --> host = "0.0.0.0", port = 5000.
print("UDP server is on port 5000...")

while True:
    data, address = server.recvfrom(1024) # server receives data from client.
    message = data.decode() # sockets carry bytes, not text --> encode before sending, decode after receiving.
    print(f"[{address[1]}] {message}")
    reply = f"Server got: {message}"
    server.sendto(reply.encode(), address) # server sends reply to client.