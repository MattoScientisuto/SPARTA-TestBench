# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: Linear Actuator Ports and Commands

# Created: September 3rd, 2024
# Last Updated: October 7th, 2024
# ============================================ #

import PathSetup

from general_fetching_scripts.SerialPortFetching import *
from general_fetching_scripts.DateTimeFetching import *

import serial
import time

# Motor serial ports
linear_actuator = serial.Serial(f'{linear_actuator_com}', baudrate=4800, timeout=0, write_timeout=0)

actuator_duration = 8 #seconds, will change later to whatever the flight needs


# Operations
# Write command for Linear Actuator    
def digitalWrite(device, command):

    device.write(command.encode())
    print(f'[{get_timestamp()}] Command sent:', command)

    # Since the linear actuator can't tell real position,
    # we just give it the time to wait during the reset
    # so the rotation reset knows when to start
    if command == 'C':
        time_print('Homing linear actuator...')
        time.sleep(10)
        digitalWrite(linear_actuator,'s')