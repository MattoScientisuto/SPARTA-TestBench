# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Linear Actuator + Arduino + Relays Tester

# Created: September 5th, 2023
# Last Updated: November 20th, 2023
# ============================================ #

import serial
import tkinter as tk
from tkinter import ttk

def digitalWrite(command):
    ser.write(command.encode())
    print('Command sent:', command)

ser = serial.Serial('COM20', baudrate=9600, timeout=1)

root = tk.Tk()
root.geometry('300x300')
frame = tk.Frame(root, width=200, height=root.winfo_height())
frame.grid(row=0, column=0)

button = ttk.Button(frame, text="Retract", command=lambda: digitalWrite('C'))
button.grid(row=0, column=0, sticky=tk.W)
button2 = ttk.Button(frame, text="Forward", command=lambda: digitalWrite('W'))
button2.grid(row=1, column=0, sticky=tk.W)
button4 = ttk.Button(frame, text="Stop", command=lambda: digitalWrite('s'))
button4.grid(row=3, column=0, sticky=tk.W)

root.mainloop()