import socket
import time
import subprocess
from datetime import date, datetime
import datetime as dt
import os
import psutil
import sys
from threading import Thread

# Redirecting stdout to a file
# sys.stdout = open("console_log_socketlistener.txt", "a")

HOST = '0.0.0.0'  # Loopback address
PORT = 3456       # Port number your server is listening on
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

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the address and port
    server_socket.bind((HOST, PORT))

    # Listen for incoming connections
    server_socket.listen()

    todays_time = datetime.now().strftime("%H:%M:%S")
    print(f'===========================================================\n START POINT OF SOCKET LISTENER LOG: {todays_date} at {todays_time}\n===========================================================')

    print("Server listening on {}:{}".format(HOST, PORT))

    # Accept incoming connections
    connection, client_address = server_socket.accept()

    with connection:
        curr_time = dt.datetime.now().strftime("%H:%M:%S")
        print(f"[{curr_time}] Connected to:", client_address)

        # Receive and process messages indefinitely
        while True:
            data = connection.recv(1024)

            # If no connection is still established between the
            # IPC/message sender and Python, it will stop

            # This should only happen at the end of flight if it somehow
            # skips over the 'safing' trigger
            if not data:
                sys.stdout.close()
                break

            
            message = data.decode().strip()
            curr_time = datetime.now().strftime("%H:%M:%S")
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
            if message == "safing":
                curr_time = datetime.now().strftime("%H:%M:%S")
                print(f'[{curr_time}] REACHED SAFING! TIME TO END THE LISTENING CYAA')
                break
