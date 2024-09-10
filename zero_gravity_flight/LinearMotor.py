# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: Linear Actuator Ports and Commands

# Created: September 3rd, 2024
# Last Updated: September 4th, 2024
# ============================================ #
from DateTimeFetching import *
import serial
import time

# Motor serial ports
linear_actuator = serial.Serial('COM5', baudrate=9600, timeout=1)

actuator_duration = 5 #seconds, will change later to whatever the flight needs


# Operations
# Write command for Linear Actuator    
def digitalWrite(device, command):
    time.sleep(0.2)
    device.write(command.encode())
    print(f'[{get_timestamp()}] Command sent:', command)

    # Since the linear actuator can't tell real position,
    # we just give it the time to wait during the reset
    # so the rotation reset knows when to start
    if command == 'C':
        time.sleep(6)