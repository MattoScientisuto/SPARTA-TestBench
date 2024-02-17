import socket

HOST = '127.0.0.1'  # Loopback address
PORT = 50155        # Port number your server is listening on

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the address and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen()

    print("Server listening on {}:{}".format(HOST, PORT))

    # Accept incoming connections
    connection, client_address = server_socket.accept()

    with connection:
        print("Connected to:", client_address)

        # Receive and process messages indefinitely
        while True:
            data = connection.recv(1024)
            if not data:
                break
            print("Received:", data.decode())
