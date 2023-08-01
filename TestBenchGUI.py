# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA New Test Bench 
# Main GUI Interface Runner

# File Created: June 13th, 2023
# Last Updated: July 26th, 2023
# ============================================ #

# Changelog:
#region    

  # 7-5-23
    # Removed 'argparse' to run the script using a terminal
     # No need for it anymore since I added the GUI
     # Would have become more irrelevant as more parts were added (i.e. torque sensor, DSP)
    # Added a gain and offset value for the load cell data
        # Calibrated by using a known weight (i.e. soil sample) and placed it on top of it
        # Trial and error: repeated until the correct weight in newtons was displayed
        
  # 7-10-23
    # Fixed issue where continuous load cell runs using the GUI resulted in timestamps not saving properly
     # Every new log file would duplicate amount of timestamp readings
     # SOLUTION: At the start of every run, clear all previously saved data in lists
    # Added JPL logo into top left corner
    
  # 7-17-23
    # Added live plot
     # Running/reading from the load cell is currently assigned to a separate thread
      # Allows the live plot to actually update (otherwise the main window freezes/stops responding)
      # BUT currently has an issue where the thread never terminates, so the whole program has to be restarted on each run
    # Removed old plot that appears after data acquisition was finished
     # No need for it anymore since we now have live plots
    # Attempted to figure out timing/performance inconsistencies
     # Still more work to do

  # 7-18-23
    # Added torque sensor reading and logging functions + live plot
    # Added a scuffed separator in between the load cell and torque sensor operations
     # I thought it would have pushed the torque sensor items to the right
     # Going to probably need blank placeholders with padding or something
     
    # Still need to figure out timing/performance inconsistencies
     # For sure when laptop is not plugged in, it reads and plots a lot slower
     # ALSO with the current DAQ tasks, I think setting it on 'CONTINUOUS' might be causing inconsistent time
      # Sometimes causes a time clock error at the end of operations
       # Can potentially screw up the overall program
    # Need to figure out how to stop animation functions once operation is over
     # Significantly slows down the other component since it's still monitoring another file
    # Need to figure out how to kill threads properly
    
    # POSSIBILITIES:
     # 1.) Thread the animation functions as well (might be easier said than done)

  # 7-19-23
    # Adjusted refresh rate on animation objects to 400ms
     # Might just have to bite the bullet and look at the lag (takes up way too much CPU space)
    # Adjusted buffer size
     # Not exactly what it affected just yet (continue looking into it)
     # Apparently higher rates will make it capture data less frequently
    # PROBABLY A TEMPORARY FIX:
     # Added a 'Restart' button 
      # Restarts the whole script and GUI to make sure the threads for both devices are properly closed
       # Allows the load cell and torque sensor to re-run properly
      # In the future, I would rather have a way for it to automatically close the threads without the user needing to know about it
     
    # Found that the occasional clock error is because the program is going too slow to keep up with the DAQ
     # Usually happens when laptop doesn't have enough power, or isn't plugged in
     # Or too much CPU power is being taken which significantly slows down reading and logging
     
    # Need to add
     # 'Currently running' indicators to show what device is currently running
     # 'Current log file' indicator to assure the user the correct log file is being used
      # Right now all of the confirmation outputs go through the terminal, which won't work later once this is an executable
     # ALSO need to calibrate torque sensor with the wrench once Bob finishes his plate to attach to it
     
   # 7-24-23
    # Changed load cell live plot to 'Depth (cm)' and 'Force (Newtons)'
     # Also inverted the y-axis
    # Added 'Date Plotted' to both figures
    
   # 7-25-23
    # Added new status displays for:
     # Current log file names
     # Running status (true or false)
     # FOR LOAD CELL: 
      # Current depth
       # Has some performance inconsistencies
       # Disabled for now
      # Maximum newton value read
      
   # 7-26-23
    # Major performance improvements
     # Forgot all about the DAQ print statements that would clog up the console
     # Average CPU performance dropped from 70-90% capacity to 10-23%
     # Also allowed the 'Current depth' meter to be re-enabled without any issues
     # Laptop can now operate at optimal performance (even when unplugged)
    
    # DSP Functions created for 0.01V and 0.5V amplitude
     # Script loads two pre-made Ivium method files and sends them to Ivium to scan
     # Will probably be adding the same status displays
      # Device connected status
      # Currently running (refer to Ivium!)
    
#endregion

# ======================== #

# IMPORTS
#region

import serial
import serial.tools.list_ports

import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits

import os
import sys
import csv

from datetime import date
import datetime as dt

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image  
import sidebar

from threading import Thread

from pyvium import Core

#endregion

# ======================== #
#   LOAD + TORQUE READING
# ======================== #
csv_list = []
torque_csv = []

strain_data = []
strain_orig = []
timestamps = []

entry_nums = []
r_count = 1

lc_running = False
ts_running = False

# Time elapsed (at the end of this method) will be the total 
total_time = 0
sample_rate = 50.0
acquisition_duration = 620 #45 is 28 seconds, 41 is mms and jsc tested 7-12
num_of_samples = int(sample_rate * acquisition_duration)

def switch_true(device):
    device.config(text='True', background='#15eb80')
    
def switch_false(device):
    device.config(text='False', background='#f05666')
    
def log_update(device):
    if device is curr_log1:
        device.config(text=csv_list[0], background='#15eb80')
    elif device is curr_log2:
        device.config(text=torque_csv[0], background='#15eb80')
    
def depth_update(i):
    curr_depth.config(text='{:.3f}'.format(entry_nums[i]))

def newton_update():
    curr_newt.config(text='{:.3f}'.format(max(strain_data)), background='white')
    
def read_load_cell():
    global total_time
    global lc_running
    global r_count
    
    with nidaqmx.Task() as ai_task:
         
        # Setup the NI cDAQ-9174 + DAQ 9237 module
        # Specify the DAQ port (find using NI-MAX)
        # Then choose the units + sample rate + acquisition type
        ai_task.ai_channels.add_ai_bridge_chan("cDAQ1Mod1/ai0")
        ai_task.ai_channels.ai_bridge_units = BridgePhysicalUnits.NEWTONS
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 2000

        # Start the task
        
        # CLEAR OLD DATA EVERY NEW RUN TO PREVENT INTERFERANCE!
        timestamps.clear()
        strain_data.clear()
        strain_orig.clear()
        entry_nums.clear()
        
        ai_task.start()
        lc_running = True
        switch_true(load_running)
        start_time = dt.datetime.now()
        
        with open(csv_list[0], 'a', newline='') as file:
            writer = csv.writer(file)
            
            for i in range(num_of_samples):
                strain = ai_task.read()     # Read current value
                true_strain = strain * -1   # Inversion (raw readings come negative for some)
                newton = (strain * (-96960)) - 1.12 # -96960 gain, 1.12 zero offset

                # print(f"Newtons: {newton}")
                now = dt.datetime.now()
                
                # Calculate current time, starting from 0 seconds
                # Then store in global timestamps list for plotting
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)
                timestamps.append(rounded_seconds)
                
                # Store newton readings
                strain_data.append(newton)
                # Also storing raw values just in case
                strain_orig.append(true_strain)
                # Store current depth
                entry_nums.append(r_count / 7500)
                depth_update(i)
                r_count+=1
                
                # Write current value to CSV
                # Real-time so that the GUI plot can keep up
                writer.writerow([timestamps[i], entry_nums[i], strain_data[i], strain_orig[i]])
            file.close()
                
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        lc_running = False
        switch_false(load_running)
        newton_update()
        print('Run Completed!')
thread_load_cell = Thread(target=read_load_cell)

# ===================================================

lbs_inches = []
raw_torque = []
torque_timestamps = []

def read_torque_sensor():
    global total_time
    global ts_running
    with nidaqmx.Task() as ai_task:
         
        # Setup the NI cDAQ-9174 + DAQ 9237 module
        # Specify the DAQ port (find using NI-MAX)
        # Then choose the units + sample rate + acquisition type
        ai_task.ai_channels.add_ai_bridge_chan("cDAQ1Mod1/ai1")
        ai_task.ai_channels.ai_bridge_units = BridgePhysicalUnits.INCH_POUNDS
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 5000
        
        # CLEAR OLD DATA EVERY NEW RUN TO PREVENT INTERFERANCE!
        torque_timestamps.clear()
        lbs_inches.clear()
        raw_torque.clear()
        
        ai_task.start()
        ts_running = True
        switch_true(torque_running)
        start_time = dt.datetime.now()
        
        with open(torque_csv[0], 'a', newline='') as file:
            writer = csv.writer(file)
            print(ts_running)
            for i in range(num_of_samples):
                torque = ai_task.read()     # Read current value
                true_torque = torque * -1   # Inversion (raw readings come negative for some reason)
                lb_inch = (torque * (-42960)) - 11.0     # (raw readings * gain) minus offset

                # print(f"Pound-inches: {lb_inch}")
                now = dt.datetime.now()
                
                # Calculate current time, starting from 0 seconds
                # Then store in global timestamps list for plotting
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)
                torque_timestamps.append(rounded_seconds)
                
                # Store newton readings
                lbs_inches.append(lb_inch)
                # Also storing raw values just in case
                raw_torque.append(true_torque)
                
                # Write current value to CSV
                # Real-time so that the GUI plot can keep up
                writer.writerow([torque_timestamps[i], lbs_inches[i], raw_torque[i]])
            file.close()
                
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        ts_running = False
        switch_false(torque_running)
        print('Run Completed!')
thread_torque_sensor = Thread(target=read_torque_sensor) 
    
# ======================== #
#     TKINTER GUI SETUP 
# ======================== #
#region

# =================
# LIVE PLOTS SETUP
# =================

#region
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
current_date = date.today().strftime("%m-%d-%Y")
fig1.text(0.01, 0.97, f"Plotted: {current_date}", ha='left', va='top', fontsize=10.5)

fig2 = Figure(figsize=(4.5,4.5), dpi=100)
fig2.subplots_adjust(left=0.19, bottom=0.15)
torque_sensor = fig2.add_subplot(111)

# Labels Setup
torque_line, = torque_sensor.plot([], [], linestyle='solid', linewidth='2', color='#e37005')
torque_sensor.set_title('Torque Sensor', weight='bold')  
torque_sensor.set_xlabel('Time Elapsed (seconds)')
torque_sensor.set_ylabel('Torque (Pound-inches)')
torque_sensor.grid()

tcurrent_date = date.today().strftime("%m-%d-%Y")
fig2.text(0.01, 0.97, f"Plotted: {tcurrent_date}", ha='left', va='top', fontsize=10.5)

#endregion

# ==================
# Animate Functions
# ==================

# Load Cell Animate Function
def animate_load_cell(i):
    global lc_running
    if csv_list and lc_running is True:
        data = pd.read_csv(csv_list[0], sep=",")
        x = data['Timestamp'] 
        y = data['Force [Newtons]'] 
        y2 = data['Depth [cm]']                            
        
        load_line.set_data(y,y2)
        load_cell.relim()
        load_cell.autoscale_view()
              
# Torque Sensor Animate Function    
def animate_torque_sensor(i):
    global ts_running
    if torque_csv and ts_running is True:
        data = pd.read_csv(torque_csv[0], sep=",")
        x = data['Timestamp (seconds)'] 
        y = data['Torque [Pound-inches]']                             
        
        torque_line.set_data(x,y)
        torque_sensor.relim()
        torque_sensor.autoscale_view()

# =================
# 'Get' CSV Names
# =================

# Get Load CSV log name
def get_csv():
    global csv_list
    input = entry.get()
    print("CSV log set to:", input)
    if len(csv_list) == 0:
        csv_list.append(input)
    else:
        csv_list[0] = input
    log_update(curr_log1)
    
    with open(f'{csv_list[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Depth [cm]", "Force [Newtons]", "Force [Raw Reading]"])
        file.close()

# Get Torque CSV log name
def get_torque_csv():
    global torque_csv
    input = torque_entry.get()
    print("CSV log set to:", input)
    if len(torque_csv) == 0:
        torque_csv.append(input)
    else:
        torque_csv[0] = input
    log_update(curr_log2)
    
    with open(torque_csv[0], 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Torque [Pound-inches]", "Torque [Raw Reading]"])
        file.close()

# =========================================
# Load Cell + Torque Sensor Run Operations
# =========================================

# Run all load cell operations (read, log, plot)    
def load_cell_run():
    thread_load_cell.start()
    
# Run all torque sensor operations (read, log, plot)    
def torque_sensor_run():
    thread_torque_sensor.start()

# ================ #
#   DSP READING
# ================ #

# EIS230724140245.imf = 0.01V for samples under 1.0% water
# EIS230724135821.imf = 0.5V for samples over 1.0% water
current_directory = os.path.dirname(os.path.abspath(__file__))

dsp_01method = 'EIS230724140245.imf'
dsp_05method = 'EIS230724135821.imf'

# Merge ivium.py directory + dsp_settings folder + chosen settings
file_path = os.path.join(current_directory, 'dsp_settings', dsp_01method)

def connect_dsp():
    Core.IV_open()
    Core.IV_connect(1)
    print(Core.IV_getdevicestatus())
    print(Core.IV_readSN())
    
def scan_op():
    print(Core.IV_readmethod(file_path))
    print(Core.IV_startmethod(file_path))

# ======================
# TKINTER WINDOW LAYOUT
# ======================

# =============
# Window/Frame 
# =============
#region
window = Tk()
window.title('New Test Bench')
# window.geometry('1000x730')
window.protocol("WM_DELETE_WINDOW")

frm = ttk.Frame(window)
frm.grid(padx=4, pady=4)




min_w = 50 # Minimum width of the frame
max_w = 140 # Maximum width of the frame
cur_width = min_w # Increasing width of the frame
expanded = False # Check if it is completely exanded

def expand():
    global cur_width, expanded
    cur_width += 10 # Increase the width by 10
    rep = window.after(5,expand) # Repeat this func every 5 ms
    frame.config(width=cur_width) # Change the width to new increase width
    if cur_width >= max_w: # If width is greater than maximum width 
        expanded = True # Frame is expended
        window.after_cancel(rep) # Stop repeating the func
        fill()

def contract():
    global cur_width, expanded
    cur_width -= 10 # Reduce the width by 10 
    rep = window.after(5,contract) # Call this func every 5 ms
    frame.config(width=cur_width) # Change the width to new reduced width
    if cur_width <= min_w: # If it is back to normal width
        expanded = False # Frame is not expanded
        window.after_cancel(rep) # Stop repeating the func
        fill()

def fill():
    if expanded: # If the frame is exanded
        # Show a text, and remove the image
        home_b.config(text='Home',image='',font=(0,21))
        set_b.config(text='Settings',image='',font=(0,21))
        ring_b.config(text='Bell Icon',image='',font=(0,21))
    else:
        # Bring the image back
        home_b.config(image=home,font=(0,21))
        set_b.config(image=settings,font=(0,21))
        ring_b.config(image=ring,font=(0,21))

# Define the icons to be shown and resize it
home = ImageTk.PhotoImage(Image.open('.\\gui_images\\home.png').resize((40,40)))
settings = ImageTk.PhotoImage(Image.open('.\\gui_images\\settings.png').resize((40,40)))
ring = ImageTk.PhotoImage(Image.open('.\\gui_images\\ring.png').resize((40,40)))

window.update() # For the width to get updated
frame = Frame(frm,bg='orange',width=50,height=window.winfo_height())
frame.grid(row=0,column=0, sticky=W) 

# Make the buttons with the icons to be shown
home_b = Button(frame,image=home,bg='orange',relief='flat')
set_b = Button(frame,image=settings,bg='orange',relief='flat')
ring_b = Button(frame,image=ring,bg='orange',relief='flat')

# Put them on the frame
home_b.grid(row=0,column=0,pady=10)
set_b.grid(row=1,column=0,pady=50)
ring_b.grid(row=2,column=0)

# Bind to the frame, if entered or left
frame.bind('<Enter>',lambda e: expand())
frame.bind('<Leave>',lambda e: contract())

# So that it does not depend on the widgets inside the frame
frame.grid_propagate(False)






def restart_program():
    python = sys.executable
    os.execl(python, 'python ', *sys.argv)

# Title
main_title = ttk.Label(frm, text="New Test Bench", font=("Arial", 18))
main_title.grid(row=1, column=9, padx=5, pady=5, sticky=NE)
# Restart Button
restart_button = ttk.Button(frm, text="Restart", command=restart_program)
restart_button.grid(row=2, column=9, padx=5, pady=5)

# Tab Control
# tab_control = ttk.Notebook(window)
# tab1 = ttk.Frame(tab_control)
# tab_control.add(tab1, text='DSP')
# tab_control.grid(row=0, column=0)
# ttk.Label(tab1, text='swag').grid(row=0, column=0)
#endregion

# ========================
# Images / Decorative
# ========================
#region
jpl_logo = Image.open('.\\gui_images\\jpl_logo_resized.png')
jpl_img = ImageTk.PhotoImage(jpl_logo)

label1 = ttk.Label(image=jpl_img)
label1.image = jpl_img
# label1.grid(row=0, column=0, padx=3, pady=5, sticky=NW)
#endregion

# ========================
# Entry + command widgets
# ========================
#region

# Load Cell
# set_csv = ttk.Label(frm, text="Set CSV log file name:", font=("Arial", 10)).grid(row=4, column=0, padx=3, pady=3)
entry = ttk.Entry(frm)
# entry.grid(row=4, column=1, padx=5, pady=8)

csv_button = ttk.Button(frm, text="Set Name", command=get_csv)
# csv_button.grid(row=4, column=2, padx=5, pady=8)

# Live Numerical Displays

# Load Cell
# log1 = ttk.Label(frm, text="Logging to: ", font=("Arial", 10)).grid(row=5, column=0)
curr_log1 = ttk.Label(frm, text='N/A', font=("Arial", 14), background='#f05666')
# curr_log1.grid(row=5, column=1, sticky=W, pady=2)

# running1 = ttk.Label(frm, text="Currently Running: ", font=("Arial Bold", 10)).grid(row=6, column=0, pady=2)
load_running = ttk.Label(frm, text=str(lc_running), font=("Arial", 14), background='#f05666')
# load_running.grid(row=6, column=1, sticky=W, pady=2)

# depth = ttk.Label(frm, text="Current Depth (cm): ", font=("Arial Bold", 10)).grid(row=7, column=0, pady=2)
curr_depth = ttk.Label(frm, text='0.00', font=("Arial", 14), background='white')
# curr_depth.grid(row=7, column=1, sticky=W, pady=2)

# newt = ttk.Label(frm, text="Greatest Force (Newton): ", font=("Arial Bold", 10)).grid(row=8, column=0, pady=2)
curr_newt = ttk.Label(frm, text='0.00', font=("Arial", 14), background='#e0e0e0')
# curr_newt.grid(row=8, column=1, sticky=W, pady=2)

run_button = ttk.Button(frm, text="Run Load Cell", command=load_cell_run)
# run_button.grid(row=5, column=2, padx=5, pady=5)


# Torque Sensor
set_tcsv = ttk.Label(frm, text="  Set torque CSV file name:", font=("Arial", 10)).grid(row=4, column=7, padx=3 ,pady=3)
torque_entry = ttk.Entry(frm)
torque_entry.grid(row=4, column=8, padx=3, pady=3)

csv_torque_button = ttk.Button(frm, text="Set Name", command=get_torque_csv)
csv_torque_button.grid(row=4, column=9, padx=3, pady=3)

run_torque_button = ttk.Button(frm, text="Run Torque Sensor", command=torque_sensor_run)
run_torque_button.grid(row=5, column=9, padx=3, pady=3)



log2 = ttk.Label(frm, text="Logging to: ", font=("Arial", 10)).grid(row=5, column=7)
curr_log2 = ttk.Label(frm, text='N/A', font=("Arial", 14), background='#f05666')
curr_log2.grid(row=5, column=8, sticky=W, pady=2)


running2 = ttk.Label(frm, text="Currently Running: ", font=("Arial Bold", 10)).grid(row=6, column=7, pady=2)
torque_running = ttk.Label(frm, text=str(lc_running), font=("Arial", 14), background='#f05666')
torque_running.grid(row=6, column=8, sticky=W, pady=2)

# Motor Controller Test Code
# Currently not in use (not until parts are assembled)

# ser = serial.Serial('COM5', baudrate=38400, bytesize=8, parity='N', stopbits=1, xonxoff=False)

# ser.write('@0M20000\r'.encode())

# def go_to():
#     ser.write('@0P50000\r'.encode())
#     ser.write('@0G\r'.encode())   
#     ser.write('@0F\r'.encode())   

# def reset_to():
#     ser.write('@0P0\r'.encode())
#     ser.write('@0G\r'.encode())
#     ser.write('@0F\r'.encode())

jog_to = ttk.Button(frm, text="Connect to DSP", command=connect_dsp)
jog_to.grid(row=5, column=5, padx=5, pady=5, sticky=N)
reset_pos = ttk.Button(frm, text="Run 0.01V Scan", command=scan_op)
reset_pos.grid(row=6, column=5, padx=5, pady=5, sticky=N)

#endregion

# ========================
#       Plot Display
# ========================
#region

canvas = FigureCanvasTkAgg(fig1, master=window)
canvas.get_tk_widget().grid(row=5, column=0, padx=5, pady=5, sticky=W)
canvas.get_tk_widget().config(borderwidth=2, relief=tk.RAISED)

canvas2 = FigureCanvasTkAgg(fig2, master=window)
canvas2.get_tk_widget().grid(row=5, column=0, padx=5, pady=5, sticky=E)
canvas2.get_tk_widget().config(borderwidth=2, relief=tk.RAISED)

#endregion

# ===========
# Main Calls
# ===========

ani = FuncAnimation(fig1, animate_load_cell, interval=1000, cache_frame_data=False)
ani2 = FuncAnimation(fig2, animate_torque_sensor, interval=1000, cache_frame_data=False)

plt.show()
window.mainloop()

#endregion