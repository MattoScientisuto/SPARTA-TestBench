###############################################################################
# Program Name: JLF_SPARTA_FeedbackActuator_SerialCommunications.py
# Author: Jared Long-Fox
# Date Last Modified: April 28, 2024
###############################################################################





#                           Imports and Settings
###############################################################################

import numpy as np #array/matrix manipulation, random numbers, analysis, etc.
from matplotlib import pyplot as plt #general plotting and data display
import serial
import time


font = {'family' : 'normal','weight' : 'normal'}  
plt.rc('font', **font) 
plt.rcParams["font.family"] = "serif"

###############################################################################



def send_distance_to_arduino(distance):
    # Convert the decimal number to bytes
    bytes_to_send = bytes(str(distance) + '\n', 'utf-8')
    # Write bytes to serial port
    ser.write(bytes_to_send)
    #print("Decimal number sent to Arduino:", decimal_number)
    
    
    
# Configure serial port
arduino_port = "COM3"  # Change this to your Arduino port
baud_rate = 9600  # Should match Arduino code baud rate
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Wait for Arduino to initialize


#desired_distance = 5. #cm
#send_distance_to_arduino(desired_distance)

#read the Arduino serial feed
try:
    while True:

        # Take user input for desired distance
        desired_distance = float(input("Enter desired distance (in cm): "))
        
        # Send the desired distance to Arduino
        send_distance_to_arduino(desired_distance)
        
        # Read a line from the serial port
        line = ser.readline().decode('utf-8').rstrip()
        
        # Print the received data
        print("Received:", line)
        
        # Wait for a short duration before reading again
        time.sleep(0.01)


        # # Read a line from the serial port
        # line = ser.readline().decode('utf-8').rstrip()
        
        # # Print the received data
        # print("Received:", line)
        
        # # Wait for a short duration before reading again
        # time.sleep(0.01)

except KeyboardInterrupt:
    # Close the serial port on keyboard interrupt
    ser.close()

