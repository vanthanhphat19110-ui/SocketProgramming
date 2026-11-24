from socket import *

SERVER = ("127.0.0.1", 5000) # (HOST, PORT)
client = socket(AF_INET, SOCK_DGRAM) # SOCK_DGRAM --> UDP.
client.settimeout(3) # UDP may lose data.
print("Type 'bye' to quit.")

while True:
    message = input("Client: ")
    if (message == "bye"): break # client left the chat.

    client.sendto(message.encode(), SERVER) # sockets carry bytes, not text --> encode before sending, decode after receiving.
    try:
        data, _ = client.recvfrom(1024) # client tries to receive data from server.
        print(f"Server: {data.decode()}")
    except timeout:
        print("no reply --> data loss ?")

client.close()