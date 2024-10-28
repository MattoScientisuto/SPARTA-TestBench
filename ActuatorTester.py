# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Linear Actuator + Arduino + Relays Tester

# Created: September 5th, 2023
# Last Updated: December 11th, 2023
# ============================================ #
import zero_gravity_flight.PathSetup
from general_fetching_scripts.SerialPortFetching import *

import serial
import tkinter as tk
from tkinter import ttk

# def digitalWrite(command):
#     ser.write(command.encode())
#     print('Command sent:', command)


ser = serial.Serial(f'{linear_actuator_com_vaccuum}', baudrate=4800)

def writeArd(message):
    ser.write(bytes(message, 'utf-8'))

root = tk.Tk()
root.geometry('300x300')
frame = tk.Frame(root, width=200, height=root.winfo_height())
frame.grid(row=0, column=0)

button = ttk.Button(frame, text="Retract", command=lambda: writeArd('C'))
button.grid(row=0, column=0, sticky=tk.W)
button2 = ttk.Button(frame, text="Forward", command=lambda: writeArd('W'))
button2.grid(row=1, column=0, sticky=tk.W)
button4 = ttk.Button(frame, text="Stop", command=lambda: writeArd('s'))
button4.grid(row=3, column=0, sticky=tk.W)

root.mainloop()