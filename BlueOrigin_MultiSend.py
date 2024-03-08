import socket
import time
import struct

# Set up the socket
multicast_group = '224.132.6.1'
port = 3456

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the time-to-live for messages to reach the network
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# Messages to send
messages = [
    "Hello",
    "How are you?",
    "This is a test message",
    "Goodbye"
]

while True:
    for message in messages:
        try:
            # Send data to the multicast group
            print('Sending "{}"'.format(message))
            sock.sendto(message.encode('utf-8'), (multicast_group, port))
            time.sleep(1)  # Delay between messages
        except Exception as e:
            print('Error:', e)

# Close the socket
sock.close()
