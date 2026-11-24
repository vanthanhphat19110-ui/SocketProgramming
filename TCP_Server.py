import socket

HOST, PORT = "0.0.0.0", 5000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SOCK_STREAM --> TCP.
server.bind((HOST, PORT))
server.listen(1) # server listens one client.
print(f"Server is listenning on port {PORT}.")
print("Waiting for a client ...")

connection, address = server.accept() # accept() returns a new socket connection and its address.
print(f"Connected by {address}. Type 'bye' to quit.")

while True:
    data = connection.recv(1024)
    if (not data or data == b"bye"): # client left the chat.
        print("Client left the chat.")
        break

    message = data.decode() # sockets carry bytes, not text --> encode before sending, decode after receiving.
    print(f"Client: {message}")

    reply = input("Server: ")
    connection.sendall(reply.encode())
    if(reply == "bye"): # server left the chat.
        print("You left the chat.")
        break

connection.close()
server.close()