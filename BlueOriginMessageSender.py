import socket
import time

HOST = '127.0.0.1'  # Loopback address
PORT = 50155        # Port number your server is listening on

# Message to send
message = ["escape", "liftoff", "meca", "separation",
            "coast", "apogee", "touchdown", "safing", "end"]
 
# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Connect to the server
    client_socket.connect((HOST, PORT))
    
    # Send the message
    for m in message:
        time.sleep(3)
        client_socket.sendall(m.encode())

print("Message sent to server:", message)
