# https://stackoverflow.com/questions/51973653/tkinter-grid-fill-empty-space

# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# GUI Interface Runner

# Created: June 13th, 2023
# Last Updated: August 1st, 2023
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
      
   # 7-31-23
    # Found a stackoverflow makeshift expanding sidebar
     # Currently building from the ground up on 'sidebar_stack.py'
      # Will migrate code back over once everything is running seamlessly
    # Added all components to CPT page
     # TESTED: data logging and plotting working, also doesn't erase any data switching page to page
     # TO DO: adjust grid positions to make it look pretty
    
    # Note to self: try to really understand how the sidebar frame and shaping works
     # Seems really helpful for making custom interfaces that need really specific details
    
   # 8-1-23
    # Completely migrated functions over to this new .py file
    # Added all components to VST page
    # Added individual output folders for CPT and DSP
     # Also includes the current date for more organization purposes
    # Added some new components to DSP page
     # 0.01V and 0.5V buttons are temporary (will be replaced with checkboxes or radio buttons)
     # Added displays for connection and device serial number
    # Fixed grid positions for CPT and VST
    
#endregion

from tkinter import *
import tkinter as tk
import tkinter as ttk
from PIL import Image, ImageTk

from datetime import date
import datetime as dt

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits

from pyvium import Core
from pyvium import Tools

import os
import sys
import csv

from threading import Thread

root = Tk()
root.title('SPARTA Test Bench')
root.geometry('650x720')

def restart_program():
    python = sys.executable
    os.execl(python, 'python ', *sys.argv)

# Home frame is set as the start up page
home_frame = Frame(root, width=200, height=root.winfo_height())
home_frame.grid(row=0, column=1, sticky=N)
cpt_frame = Frame(root, width=200, height=root.winfo_height())
vst_frame = Frame(root, width=200, height=root.winfo_height())
dsp_frame = Frame(root, width=200, height=root.winfo_height())

min_w = 50 # Minimum width of the frame
max_w = 150 # Maximum width of the frame
cur_width = min_w # Increasing width of the frame
expanded = False # Check if it is completely exanded

def expand():
    global cur_width, expanded
    cur_width += 10 # Increase the width by 10
    rep = root.after(5,expand) # Repeat this func every 5 ms
    frame.config(width=cur_width) # Change the width to new increase width
    if cur_width >= max_w: # If width is greater than maximum width 
        expanded = True # Frame is expended
        root.after_cancel(rep) # Stop repeating the func
        fill()

def contract():
    global cur_width, expanded
    cur_width -= 10 # Reduce the width by 10 
    rep = root.after(5,contract) # Call this func every 5 ms
    frame.config(width=cur_width) # Change the width to new reduced width
    if cur_width <= min_w: # If it is back to normal width
        expanded = False # Frame is not expanded
        root.after_cancel(rep) # Stop repeating the func
        fill()

def fill():
    if expanded: # If the frame is expanded
        # Show a text, and remove the image
        home_b.config(text='Home',image=home,font=(0,15), relief='raised')
        cpt_b.config(text='Cone\nPenetrator',image='',font=(0,15), relief='raised')
        vst_b.config(text='Vane Shear\nTester',image='',font=(0,15), relief='raised')
        dsp_b.config(text='Dielectric\nSpectrometer',image='',font=(0,15), relief='raised')
    else:
        # Bring the image back
        home_b.config(image=home,font=(0,15), relief='flat')
        cpt_b.config(image=cpt,font=(0,15), relief='flat')
        vst_b.config(image=vst,font=(0,15), relief='flat')
        dsp_b.config(image=dsp,font=(0,15), relief='flat')

def show_page(page):
    # Hide all pages
    home_frame.grid_forget()
    cpt_frame.grid_forget()
    vst_frame.grid_forget()
    dsp_frame.grid_forget()

    # Show the selected page
    if page == "Home":
        home_frame.grid(row=0, column=1, sticky=N)

    elif page == "CPT":
        cpt_frame.grid(row=0, column=1, sticky=N)   

    elif page == "VST":
        vst_frame.grid(row=0, column=1, sticky=N)   

    elif page == "DSP":
        dsp_frame.grid(row=0, column=1, sticky=N)   

# Define the icons to be shown and resize it
home = ImageTk.PhotoImage(Image.open('.\\gui_images\\home.png').resize((40,40)), Image.Resampling.LANCZOS)
cpt = ImageTk.PhotoImage(Image.open('.\\gui_images\\cpt.png').resize((40,40)), Image.Resampling.LANCZOS)
vst = ImageTk.PhotoImage(Image.open('.\\gui_images\\vst.png').resize((40,40)), Image.Resampling.LANCZOS)
dsp = ImageTk.PhotoImage(Image.open('.\\gui_images\\dsp.png').resize((40,40)), Image.Resampling.LANCZOS)

root.update() # For the width to get updated
frame = Frame(root,bg='orange',width=50,height=root.winfo_height())
frame.grid(row=0,column=0) 

# Make the buttons with the icons to be shown
home_b = Button(frame,image=home,bg='orange',relief='flat', command=lambda: show_page("Home"))
cpt_b = Button(frame,image=cpt,bg='orange',relief='flat',   command=lambda: show_page("CPT"))
vst_b = Button(frame,image=vst,bg='orange',relief='flat',   command=lambda: show_page("VST"))
dsp_b = Button(frame,image=dsp,bg='orange',relief='flat',   command=lambda: show_page("DSP"))

# Put them on the frame
home_b.grid(row=0,column=0, pady=15)
cpt_b.grid(row=1,column=0, pady=15)
vst_b.grid(row=2,column=0, pady=15)
dsp_b.grid(row=3,column=0, pady=15)

# Bind to the frame, if entered or left
frame.bind('<Enter>',lambda e: expand())
frame.bind('<Leave>',lambda e: contract())

# So that it does not depend on the widgets inside the frame
frame.grid_propagate(False)

# ========================================================================

csv_list = []
torque_csv = []
dsp_idf = []

# Directory adjusts to any PC
current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Data output directories for each component
cpt_dir = f'.\\data_output\\cpt\\{todays_date}'
vst_dir = f'.\\data_output\\vst\\{todays_date}'
dsp_dir = f'.\\data_output\\dsp\\{todays_date}'

strain_data = []
strain_orig = []
timestamps = []

entry_nums = []
r_count = 1

lc_running = False
ts_running = False

dsp_connected = False

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
    elif device is curr_log3:
        device.config(text=dsp_idf[0], background='#15eb80')
    
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
        
        with open(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', 'a', newline='') as file:
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

# Torque Sensor Read
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
        
        with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'a', newline='') as file:
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

# ================ #
#   DSP READING
# ================ #
#region

def device_update(device, serial):
    device.config(text=serial, background='#15eb80')

# EIS230724140245.imf = 0.01V for samples under 1.0% water
# EIS230724135821.imf = 0.5V for samples over 1.0% water
dsp_001method = 'EIS230724140245.imf'
dsp_05method = 'EIS230724135821.imf'

# Merge ivium.py directory + dsp_settings folder + chosen settings
dsp_methods = os.path.join(current_directory, 'dsp_settings', dsp_001method)

# Connect to DSP
def connect_dsp():
    global dsp_connected
    
    Core.IV_open()
    # '1' means to connect
    Core.IV_connect(1)
    
    # '-1' == IviumSoft isn't opened
    # '0'  == Not connected to IviumSoft yet
    # '1'  == Connected to IviumSoft, idle
    # '2'  == Connected to IviumSoft, busy
    status = Core.IV_getdevicestatus()
    print(Core.IV_getdevicestatus())
    if status == -1:
        ttk.messagebox.showinfo("Error", 'Please open IviumSoft if you want to connect to a device!')
    elif status == 1:
        dsp_connected = True
        switch_true(dsp_status)
        device_serial = (Core.IV_readSN())
        device_update(dsp_device, device_serial[1])
    elif status == 3:
        ttk.messagebox.showinfo("Error", 'No device detected!')

# Start the scan operation using the selected preset method
# TEMPORARY: currently statically set to 0.01V method
def scan_op():
    print(Core.IV_readmethod(dsp_methods))
    print(Core.IV_startmethod(dsp_methods))

# After the scanning finishes, user can save the data to the output folder
def save_idf():
    if len(dsp_idf) == 0:
        tk.messagebox.showinfo("Error", 'No name has been set for the log file!')
    else:
        dsp_output = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf[0])
        print(Core.IV_savedata(dsp_output))

#endregion

# =================
# LIVE PLOTS SETUP
# =================

# Load Cell
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
#endregion

# Torque Sensor
#region

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
        data = pd.read_csv(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', sep=",")
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
        data = pd.read_csv(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', sep=",")
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
    global cpt_dir
    
    input = entry.get()
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(csv_list) == 0:
        csv_list.append(input)
    else:
        csv_list[0] = input
    log_update(curr_log1)
    print("CSV log set to:", input)
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(cpt_dir):
        os.makedirs(cpt_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Depth [cm]", "Force [Newtons]", "Force [Raw Reading]"])
        file.close()

# Get Torque CSV log name
def get_torque_csv():
    global torque_csv
    global vst_dir
    input = torque_entry.get()
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(torque_csv) == 0:
        torque_csv.append(input)
    else:
        torque_csv[0] = input
    log_update(curr_log2)
    print("CSV log set to:", input)
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(vst_dir):
        os.makedirs(vst_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Torque [Pound-inches]", "Torque [Raw Reading]"])
        file.close()

# Get Torque CSV log name
def get_dsp_idf():
    global dsp_idf
    input = dsp_entry.get()
    
    # If the list of idfs is empty, append
    # Otherwise, replace the current stored idf
    if len(dsp_idf) == 0:
        dsp_idf.append(input)
    else:
        dsp_idf[0] = input
    log_update(curr_log3)
    print("IDF log set to:", input)
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(dsp_dir):
        os.makedirs(dsp_dir)
        
# =========================================
# Load Cell + Torque Sensor Run Operations
# =========================================

# Run all load cell operations (read, log, plot)    
def load_cell_run():
    thread_load_cell.start()

# Run all torque sensor operations (read, log, plot)    
def torque_sensor_run():
    thread_torque_sensor.start()
    
# ===================
#       Frames
# ===================

# Homepage
#region
jpl_logo = Image.open('.\\gui_images\\jpl_logo_resized.png')
jpl_img = ImageTk.PhotoImage(jpl_logo)
label1 = ttk.Label(home_frame,image=jpl_img)
label1.image = jpl_img
label1.grid(row=0, column=0, padx=5, pady=5, sticky=NW)

# Title
main_title = ttk.Label(home_frame, text="SPARTA Test Bench Home Page", font=("Arial", 18))
main_title.grid(row=1, column=0, padx=5, pady=5, sticky=NW)  # Update column to 0

# Restart Button
restart_button = ttk.Button(home_frame, text="Restart", command=restart_program)
restart_button.grid(row=2, column=0, padx=5, pady=5, sticky=NW)  # Update column to 0

#endregion

# CPT page
#region
cpt_test = ttk.Label(cpt_frame, text='Cone Penetrator', font=("Arial", 18)) 
cpt_test.grid(row=0,column=0, padx=5, pady=6)

set_csv = ttk.Label(cpt_frame, text="Set load log name (include .csv): ", font=("Arial", 10)).grid(row=1, column=0, padx=3, pady=3)
entry = ttk.Entry(cpt_frame)
entry.grid(row=1, column=1, padx=3, pady=3, sticky=W)

csv_button = ttk.Button(cpt_frame, text="Set Name", command=get_csv)
csv_button.grid(row=1, column=2, padx=3, pady=3, sticky=W)

run_button = ttk.Button(cpt_frame, text="Run Load Cell", command=load_cell_run)
run_button.grid(row=2, column=2, padx=3, pady=3, sticky=W)

log1 = ttk.Label(cpt_frame, text="Logging to: ", font=("Arial", 10)).grid(row=3, column=0)
curr_log1 = ttk.Label(cpt_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log1.grid(row=3, column=1, sticky=W, pady=2)

running1 = ttk.Label(cpt_frame, text="Currently Running: ", font=("Arial Bold", 10)).grid(row=4, column=0, pady=2)
load_running = ttk.Label(cpt_frame, text=str(lc_running), font=("Arial", 14), background='#f05666', relief='groove')
load_running.grid(row=4, column=1, sticky=W, pady=2)

depth = ttk.Label(cpt_frame, text="Current Depth (cm): ", font=("Arial Bold", 10)).grid(row=5, column=0, pady=2)
curr_depth = ttk.Label(cpt_frame, text='0.00', font=("Arial", 14), background='white', relief='groove')
curr_depth.grid(row=5, column=1, sticky=W, pady=2)

newt = ttk.Label(cpt_frame, text="Greatest Force (Newton): ", font=("Arial Bold", 10)).grid(row=6, column=0, pady=2)
curr_newt = ttk.Label(cpt_frame, text='0.00', font=("Arial", 14), background='#e0e0e0', relief='ridge')
curr_newt.grid(row=6, column=1, sticky=W, pady=2)

#endregion

# VST page
#region

vst_test = ttk.Label(vst_frame, text='Vane Shear Tester', font=("Arial", 18)) 
vst_test.grid(row=0,column=0, padx=5, pady=6)

set_tcsv = ttk.Label(vst_frame, text="Set torque log name (include .csv):", font=("Arial", 10)).grid(row=1, column=0, padx=3, pady=3)
torque_entry = ttk.Entry(vst_frame)
torque_entry.grid(row=1, column=1, padx=3, pady=3, sticky=W)

csv_torque_button = ttk.Button(vst_frame, text="Set Name", command=get_torque_csv)
csv_torque_button.grid(row=1, column=2, padx=3, pady=3, sticky=W)

run_torque_button = ttk.Button(vst_frame, text="Run Torque Sensor", command=torque_sensor_run)
run_torque_button.grid(row=2, column=2, padx=3, pady=3, sticky=W)

log2 = ttk.Label(vst_frame, text="Logging to: ", font=("Arial", 10)).grid(row=3, column=0)
curr_log2 = ttk.Label(vst_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log2.grid(row=3, column=1, sticky=W, pady=2)

running2 = ttk.Label(vst_frame, text="Currently Running: ", font=("Arial Bold", 10)).grid(row=4, column=0, pady=2)
torque_running = ttk.Label(vst_frame, text=str(lc_running), font=("Arial", 14), background='#f05666', relief='groove')
torque_running.grid(row=4, column=1, sticky=W, pady=2)

#endregion

# DSP page
#region

dsp_test = ttk.Label(dsp_frame, text='Dielectric Spectrometer', font=("Arial", 18)) 
dsp_test.grid(row=0,column=0, padx=5, pady=6)

dsp_connection = ttk.Label(dsp_frame, text="Connected to Ivium: ", font=("Arial Bold", 10)).grid(row=1, column=0, pady=2)
dsp_status = ttk.Label(dsp_frame, text=str(dsp_connected), font=("Arial", 14), background='#f05666', relief='groove')
dsp_status.grid(row=1, column=1, sticky=W, pady=2)

dsp_device_status = ttk.Label(dsp_frame, text="Device Serial: ", font=("Arial Bold", 10)).grid(row=2, column=0, pady=2)
dsp_device = ttk.Label(dsp_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
dsp_device.grid(row=2, column=1, sticky=W, pady=2)

set_dcsv = ttk.Label(dsp_frame, text="Set DSP log name (include .idf):", font=("Arial", 10)).grid(row=3, column=0, padx=3, pady=10)
dsp_entry = ttk.Entry(dsp_frame)
dsp_entry.grid(row=3, column=1, pady=5, sticky=W)

dsp_torque_button = ttk.Button(dsp_frame, text="Set Name", command=get_dsp_idf)
dsp_torque_button.grid(row=3, column=2, padx=3, pady=3, sticky=W)

log3 = ttk.Label(dsp_frame, text="Logging to: ", font=("Arial", 10)).grid(row=4, column=0)
curr_log3 = ttk.Label(dsp_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log3.grid(row=4, column=1, sticky=W, pady=2)

dsp_connect = ttk.Button(dsp_frame, text="Connect to DSP", command=connect_dsp)
dsp_connect.grid(row=5, column=0, padx=5, pady=5, sticky=N)
dsp_scan = ttk.Button(dsp_frame, text="Run 0.01V Scan", command=scan_op)
dsp_scan.grid(row=6, column=0, padx=5, pady=5, sticky=N)
dsp_scan2 = ttk.Button(dsp_frame, text="Save .idf File", command=save_idf)
dsp_scan2.grid(row=7, column=0, padx=5, pady=5, sticky=N)


csv_torque_button = ttk.Button(vst_frame, text="Set Name", command=get_torque_csv)
csv_torque_button.grid(row=1, column=2, padx=3, pady=3, sticky=W)
#endregion

# =======================
# Plots for every page
# =======================
#region
canvas = FigureCanvasTkAgg(fig1, master=cpt_frame)
canvas.get_tk_widget().grid(row=7, column=0, columnspan=3, padx=30, pady=15)
canvas.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE)

canvas2 = FigureCanvasTkAgg(fig2, master=vst_frame)
canvas2.get_tk_widget().grid(row=5, column=0, columnspan=3, padx=30, pady=15)
canvas2.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE)
#endregion


ani = FuncAnimation(fig1, animate_load_cell, interval=1000, cache_frame_data=False)
ani2 = FuncAnimation(fig2, animate_torque_sensor, interval=1000, cache_frame_data=False)
plt.show()
root.mainloop()