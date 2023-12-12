# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Torque Motor (Anaheim Automation) Tester

# Created: December 11th, 2023
# Last Updated: December 11th, 2023
# ============================================ #

import serial
import tkinter as tk

stepper = serial.Serial('COM6', baudrate=38400, bytesize=8, parity='N', stopbits=1, xonxoff=False)

def go_to():
    stepper.write('@0A200\r'.encode())
    stepper.write('@0B200\r'.encode())
    stepper.write('@0M10000\r'.encode())
    stepper.write('@0P75000\r'.encode())
    stepper.write('@0G\r'.encode())   
    stepper.write('@0F\r'.encode())   
    print('Rotating forward...')
def reset():
    stepper.write('@0P0\r'.encode())
    stepper.write('@0G\r'.encode())
    stepper.write('@0F\r'.encode())
    print('Resetting position...')
    
root = tk.Tk()
root.geometry('300x300')
frame = tk.Frame(root, width=200, height=root.winfo_height())
frame.grid(row=0, column=0)

button = tk.Button(frame, text="Jog to Position", command=go_to)
button.grid(row=0, column=0, sticky=tk.W)
button2 = tk.Button(frame, text="Reset Position", command=reset)
button2.grid(row=1, column=0, sticky=tk.W)

root.mainloop()