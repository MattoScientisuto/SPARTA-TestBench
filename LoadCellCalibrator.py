# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Load Cell Calibrator

# Created: January 8th, 2023
# Last Updated: January 8th, 2023
# ============================================ #

from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
import webbrowser

from datetime import date, datetime
import datetime as dt
import time

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits, RTDType, ExcitationSource, TemperatureUnits, ResistanceConfiguration

from pyvium import Core
from pyvium import Tools

import os
import sys
import csv

import serial

from threading import Thread

import subprocess

root = Tk()
root.title('SPARTA Test Bench')
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.state('zoomed')

aio_frame = Frame(root, width=200, height=root.winfo_height())
aio_frame.grid(row=0, column=1, sticky=N)
folders = ImageTk.PhotoImage(Image.open('.\\gui_images\\data_folder.png').resize((40,40)), Image.Resampling.LANCZOS)

def open_folder(comp_path):
    os.startfile(comp_path)

# =======================
# Read Setup and Methods
# =======================
current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")
cpt_dir = f'.\\data_output\\cpt\\{todays_date}'

sample_rate = 1655
acquisition_duration = 1000

csv_list = []
strain_data = []
entry_nums = []

lc_running = False
cpt_estop_flag = False

def log_update(device):
    if device is curr_log1:
        device.config(text=csv_list[0], background='#15eb80')

def get_csv():
    global csv_list
    global cpt_dir
    
    input = entry.get() + '.csv'
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(csv_list) == 0:
        csv_list.append(input)
        print("Load CSV set to:", input)
    else:
        csv_list[0] = input
        print("Load CSV replaced with:", input)
    log_update(curr_log1)
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(cpt_dir):
        os.makedirs(cpt_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Depth [cm]", "Force [Newtons]", "Force [Raw Reading]"])
        file.close()

def switch_true(device):
    device.config(text='True', background='#15eb80')
    
def switch_false(device):
    device.config(text='False', background='#f05666')

def read_load_cell():
    
    global total_time
    global lc_running
    global r_count
    global entry_nums
    
    cpt_samples = int(sample_rate * acquisition_duration)
    
    with nidaqmx.Task() as ai_task:
         
        # Setup the NI cDAQ-9174 + DAQ 9237 module
        # Specify the DAQ port (find using NI-MAX)
        # Then choose the units + sample rate + acquisition type
        ai_task.ai_channels.add_ai_bridge_chan("cDAQ2Mod1/ai0")
        ai_task.ai_channels.ai_bridge_units = BridgePhysicalUnits.NEWTONS
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 2000

        # Start the task
        
        # CLEAR/RESET OLD DATA EVERY NEW RUN TO PREVENT INTERFERANCE!
        entry_nums.clear()
        r_count = 1
        
        ai_task.start()

        lc_running = True
        switch_true(load_running)
        start_time = dt.datetime.now()
        
        with open(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', 'a', newline='') as file:

            writer = csv.writer(file)
            
            for i in range(cpt_samples):
                strain = ai_task.read()     # Read current value
                true_strain = strain * -1   # Inversion (raw readings come negative for some)
                newton = (strain * (-96960)) - 9.25 # -96960 gain, 9.25 offset
                cdepth = r_count / 1732     # About 7705 data points per centimeter at 3 Volts

                now = dt.datetime.now()
                
                # Calculate current time, starting from 0 seconds
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)

                strain_data.append(newton)
                r_count+=1
                
                # Write current value to CSV
                # Real-time so that the GUI plot can keep up
                writer.writerow([rounded_seconds, cdepth, newton, true_strain])
                
                # If E-STOP condition is flagged:
                if cpt_estop_flag:
                    print("Emergency stop actuator!")
                    break
                
            file.close()
        
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        lc_running = False
        switch_false(load_running)
        print('CPT Run Completed!')
        tk.messagebox.showinfo("CPT Run Completed", "Total time elapsed: {:.3f} seconds".format(total_time))

def load_cell_run():
    global cpt_estop_flag
    cpt_estop_flag = False
    thread_cpt = Thread(target=read_load_cell)
    thread_cpt.start()


# =================
# LIVE PLOTS SETUP
# =================

fig1 = Figure(figsize=(4.5,4.5), dpi=100)
fig1.subplots_adjust(left=0.19, bottom=0.15)
load_cell = fig1.add_subplot(111)

# Labels Setup
load_line, = load_cell.plot([], [], linestyle='solid', linewidth='2')
load_cell.set_title('Load Cell', weight='bold')  
load_cell.set_xlabel('Force (Newtons)')
load_cell.set_ylabel('Depth (cm)')
load_cell.invert_yaxis()
load_cell.grid()

fig1.text(0.01, 0.97, f"Plotted: {todays_date}", ha='left', va='top', fontsize=10.5)

# Load Cell Animate Function
def animate_load_cell(i):
    global lc_running
    if csv_list and lc_running is True:
        data = pd.read_csv(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', sep=",")
        x = data['Timestamp'] 
        y = data['Force [Newtons]'] 
        y2 = data['Depth [cm]']                            
        
        load_line.set_data(y,y2)
        load_cell.relim()
        load_cell.autoscale_view()

# ==================
# Button Placements
# ==================

cpt_var = tk.StringVar()

cpt_test = tk.Label(aio_frame, text='Cone Penetrator', font=("Arial", 18)) 
cpt_test.grid(row=0,column=0, padx=5, pady=6)

set_csv = tk.Label(aio_frame, text="Set load log name: ", font=("Arial", 10)).grid(row=1, column=0, padx=3, pady=3)
entry = tk.Entry(aio_frame, textvariable=cpt_var)
entry.grid(row=1, column=1, padx=3, pady=3, sticky=W)

csv_button = tk.Button(aio_frame, text="Set Name", command=get_csv)
csv_button.grid(row=1, column=2, padx=3, pady=3, sticky=W)

run_button = tk.Button(aio_frame, text="Run Cone Penetrator", command=load_cell_run)
run_button.grid(row=2, column=2, padx=3, pady=3, sticky=W)

log1 = tk.Label(aio_frame, text="Logging to: ", font=("Arial", 10))
log1.grid(row=4, column=0)
curr_log1 = tk.Label(aio_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log1.grid(row=4, column=1, sticky=W, pady=2)

running1 = tk.Label(aio_frame, text="Currently Running: ", font=("Arial Bold", 10))
running1.grid(row=5, column=0, pady=2)
load_running = tk.Label(aio_frame, text=str(lc_running), font=("Arial", 14), background='#f05666', relief='groove')
load_running.grid(row=5, column=1, sticky=W, pady=2)

# Emergency Stop should send a stop code to the relays, then stop/finish the load cell reading
def cpt_estop():
    global cpt_estop_flag
    cpt_estop_flag = True
    
act_estop = tk.Button(aio_frame, text="Stop Operation", bg="#ffcdc9", command=cpt_estop)
act_estop.grid(row=4, column=2, sticky=W)

cpt_folder = tk.Button(aio_frame, image=folders, command=lambda:open_folder('.\\data_output\\cpt'))
cpt_folder.grid(row=6, column=2)

canvas = FigureCanvasTkAgg(fig1, master=aio_frame)
canvas.get_tk_widget().grid(row=7, column=0, columnspan=3, padx=30, pady=20)
canvas.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE)
ani = FuncAnimation(fig1, animate_load_cell, interval=1000, cache_frame_data=False)
plt.show()

root.mainloop()