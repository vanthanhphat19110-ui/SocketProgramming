import socket

HOST, PORT = "127.0.0.1", 5000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM --> TCP.
client.connect((HOST, PORT)) # client opens a connection to server by TCP handshake.
print("Connected to server. Type 'bye' to quit.")

while True:
    message = input("Client: ")
    client.sendall(message.encode()) # sockets carry bytes, not text --> encode before sending, decode after receiving.
    if (message == "bye"): # client left the chat.
        print("You left the chat.")
        break

    data = client.recv(1024) # client waits for a reply from server.
    if (not data or data == b"bye"): # server left the chat.
        print("Server left the chat.")
        break
    reply = data.decode()
    print(f"Server: {reply}")

client.close()