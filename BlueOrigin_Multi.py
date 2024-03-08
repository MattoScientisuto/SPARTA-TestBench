import socket
import struct

# Set up the socket
multicast_group = '224.132.6.1'
port = 3456

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Set the time-to-live for messages to reach the network
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# Bind the socket to the interface
sock.bind(('', port))

# Tell the operating system to add the socket to the multicast group
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Receive/respond loop
while True:
    print('\nWaiting to receive message...')
    data, address = sock.recvfrom(1024)

    print('Received {} bytes from {}'.format(len(data), address))
    print(data.decode('utf-8'))

# Close the socket
sock.close()
