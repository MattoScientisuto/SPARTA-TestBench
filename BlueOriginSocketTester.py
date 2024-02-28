import socket
import time
import subprocess
from datetime import date, datetime
import datetime as dt
import os
import psutil

HOST = '10.132.5.30'  # Loopback address
PORT = 80        # Port number your server is listening on

# Start IviumSoft.exe
def start_ivium():
    ivium_path = os.path.join(os.path.dirname(__file__), 'start_ivium.bat')
    subprocess.call([ivium_path])
    ivium_wait()
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'Ivium successfully started at: {time_now}')
# Check if IviumSoft is open yet
def ivium_wait():
    while True:
        ivium_status = "IviumSoft.exe" in (i.name() for i in psutil.process_iter()) 
        
        if ivium_status == True:
            time.sleep(10)
            return ivium_status
            
        time_now = dt.datetime.now().strftime("%H:%M:%S")
        print(f'Ivium still starting up at: {time_now}\nCheck again in 10 seconds...')
        time.sleep(10)
# Start IviumSoft.exe
def start_flightvst():
    fvst_path = os.path.join(os.path.dirname(__file__), 'start_BlueOriginVST.bat')
    subprocess.call([fvst_path])
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'[{time_now}] Calling VST batch...')


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

            # If no connection is still established between the
            # IPC/message sender and Python, it will stop
            if not data:
                break
            
            message = data.decode().strip()

            if message == "escape_enabled'":
                curr_time = datetime.now().strftime("%H:%M:%S")
                print(f'[{curr_time}] REACHED ESCAPE ENABLED!')
            if message == "meco":
                curr_time = datetime.now().strftime("%H:%M:%S")
                print(f'[{curr_time}] REACHED MECO!')
                start_ivium()
            if message == "coast_start":
                curr_time = datetime.now().strftime("%H:%M:%S")
                print(f'[{curr_time}] REACHED COAST_START!')
                start_flightvst()
            if message == "safing":
                curr_time = datetime.now().strftime("%H:%M:%S")
                print(f'[{curr_time}] REACHED SAFING!')

            print("Received:", message)
