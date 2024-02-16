import socket

HOST = '127.0.0.1'  # Loopback address
PORT = 50155        # Port number your server is listening on

# Message to send
message = "YO WE'RE AT ZERO GRAVITY"

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Connect to the server
    client_socket.connect((HOST, PORT))
    
    # Send the message
    client_socket.sendall(message.encode())

print("Message sent to server:", message)
