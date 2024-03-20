# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin DSP Sequence: IPC UDP Listener

# Created: February 16th, 2024
# Last Updated: March 8th, 2024
# ============================================ #

import socket
import struct
import subprocess
from datetime import date, datetime
import datetime as dt
import os
import sys
from threading import Thread

# Redirecting stdout to a file
sys.stdout = open("console_log_socketlistener.txt", "a")

todays_date = date.today().strftime("%m-%d-%Y")

# Start IviumSoft.exe
def start_flightvst():
    fvst_path = os.path.join(os.path.dirname(__file__), 'start_BlueOriginVST.bat')
    subprocess.call([fvst_path])

# Threading the VST batch file so it won't halt 
# or disrupt the reading of any other incoming
# IPC signals while it's still rotating/running.
def thread_flightvst():
    thread_vst = Thread(target=start_flightvst) 
    thread_vst.start()

# Set up the socket
multicast_group = '224.132.6.1'
port = 3761

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

todays_time = datetime.now().strftime("%H:%M:%S")
print(f'===========================================================\n START POINT OF SOCKET LISTENER LOG: {todays_date} at {todays_time}\n===========================================================')

# Receive/respond loop
while True:
    print('\nWaiting to receive flight event...')
    data, address = sock.recvfrom(1024)

    message = data.decode('utf-8')
    curr_time = datetime.now().strftime("%H:%M:%S")
    print('Received {} bytes from {}'.format(len(data), address))
    print(f'[{curr_time}] Received: {message}')
    
    if message == "escape_enabled":
        curr_time = datetime.now().strftime("%H:%M:%S")
        print(f'[{curr_time}] REACHED ESCAPE ENABLED!')
    if message == "meco":
        curr_time = datetime.now().strftime("%H:%M:%S")
        print(f'[{curr_time}] REACHED MECO!')
    if message == "coast_start":
        curr_time = datetime.now().strftime("%H:%M:%S")
        print(f'[{curr_time}] REACHED COAST_START!')
        print(f'[{curr_time}] Starting VST batch now!')
        thread_flightvst()

    # Once the flight reaches 'safing', we can safely break,
    # close out, and save our event logging
    if message == "drogue_chutes":
        curr_time = datetime.now().strftime("%H:%M:%S")
        print(f'[{curr_time}] REACHED DROGUE CHUTES! TIME TO END THE LISTENING CYAA')
        sys.stdout.close()
        sock.close()
        break

# Close the socket

