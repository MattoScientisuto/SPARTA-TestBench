import socket
import time

HOST = '10.132.5.30'  # Loopback address
PORT = 80        # Port number your server is listening on

# Message to send
message = ["escapematt", "liftoff", "meca", "separation",
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
