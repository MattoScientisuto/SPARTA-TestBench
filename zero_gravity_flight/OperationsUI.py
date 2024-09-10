# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA  
# Zero Gravity: Operations Interface

# Created: September 5th, 2023
# Last Updated: December 11th, 2023
# ============================================ #

import tkinter as tk
from tkinter import ttk
import os
import subprocess

def start_zgbatch(batch_name):
    zgbatch = os.path.join(os.path.dirname(__file__), f'{batch_name}')
    subprocess.call([zgbatch])

root = tk.Tk()
root.geometry('300x300')
frame = tk.Frame(root, width=200, height=root.winfo_height())
frame.grid(row=0, column=0)

button = ttk.Button(frame, text="CPT Operation", command=lambda: start_zgbatch('CPT_Operation.bat'))
button.grid(row=0, column=0)
button2 = ttk.Button(frame, text="VST Operation", command=lambda: start_zgbatch('admin.bat'))
button2.grid(row=1, column=0)
button3 = ttk.Button(frame, text="CPT Reset", command=lambda: start_zgbatch('CPT_Reset.bat'))
button3.grid(row=2, column=0)
button4 = ttk.Button(frame, text="VST Reset", command=lambda: start_zgbatch('VST_Reset.bat'))
button4.grid(row=3, column=0)

root.mainloop()