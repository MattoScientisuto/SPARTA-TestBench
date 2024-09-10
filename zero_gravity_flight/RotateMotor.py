# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: Rotation Motor Ports and Commands

# Created: September 3rd, 2024
# Last Updated: September 9th, 2024
# ============================================ #
from DateTimeFetching import *

import serial
import time

vst_seconds   = 20
step_position = 67 * (vst_seconds)
    
stepper = serial.Serial(
        port='COM11',
        baudrate=38400,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE, 
        stopbits=serial.STOPBITS_ONE,
        timeout=0,
        write_timeout=0,
)


def speeds_setup():

    stepper.write('@0B67\r'.encode())
    time_print('Base speed set to 67')
    time.sleep(1)
    stepper.write('@0M67\r'.encode())
    time_print('Max speed set to 67')
    time.sleep(1)
    stepper.write('@0J67\r'.encode())
    time_print('Jog speed set to 67')
    time.sleep(1)
    stepper.write('@0+\r'.encode())
    time_print('Direction set to clockwise+')
    time.sleep(1)

    stepper.close()


# Operations

def rotate_forward():

    stepper.write(f'@0N{step_position}\r'.encode())
    time.sleep(1)
    time_print('Position set to ...')
    stepper.write('@0G\r'.encode())
    time.sleep(1)
    stepper.write('@0F\r'.encode())
    time_print('Rotating forward...')   
    

def rotate_reset():

    # Reset at motor default speed, otherwise it'd take too long
    stepper.write('@0B500\r'.encode())
    time_print('Base speed set to 500')
    time.sleep(1)
    stepper.write('@0M1500\r'.encode())
    time_print('Max speed set to 500')
    time.sleep(1)
    stepper.write('@0J1500\r'.encode())
    time_print('Jog speed set to 500')
    time.sleep(1)
    stepper.write('@0P0\r'.encode())
    time_print('Position set to HOME')
    time.sleep(1)
    stepper.write('@0G\r'.encode())
    stepper.write('@0F\r'.encode())


    time_print('Resetting position...')
    time.sleep(2)

    stepper.close()