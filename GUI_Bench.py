# https://stackoverflow.com/questions/51973653/tkinter-grid-fill-empty-space

# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# GUI Interface Runner

# Created: June 13th, 2023
# Last Updated: September 11th, 2023
# ============================================ #

#region
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

root = Tk()
root.title('SPARTA Test Bench')
root.geometry('650x740')
#endregion

def open_url(url):
    webbrowser.open_new_tab(url)
    
def open_folder(comp_path):
    os.startfile(comp_path)

# Home frame is set as the start up page
home_frame = Frame(root, width=200, height=root.winfo_height())
home_frame.grid(row=0, column=1, sticky=N)
cpt_frame = Frame(root, width=200, height=root.winfo_height())
vst_frame = Frame(root, width=200, height=root.winfo_height())
dsp_frame = Frame(root, width=200, height=root.winfo_height())
tcp_frame = Frame(root, width=200, height=root.winfo_height())
imu_frame = Frame(root, width=200, height=root.winfo_height())

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
        tcp_b.config(text='Thermal\nConductivity\nProbe',image='',font=(0,15), relief='raised')
        imu_b.config(text='Inertial\nMeasurement\nUnit',image='',font=(0,15), relief='raised')
    else:
        # Bring the image back
        home_b.config(image=home,font=(0,15), relief='flat')
        cpt_b.config(image=cpt,font=(0,15), relief='flat')
        vst_b.config(image=vst,font=(0,15), relief='flat')
        dsp_b.config(image=dsp,font=(0,15), relief='flat')
        tcp_b.config(image=tcp,font=(0,15), relief='flat')
        imu_b.config(image=imu,font=(0,15), relief='flat')

def show_page(page):
    # Hide all pages
    home_frame.grid_forget()
    cpt_frame.grid_forget()
    vst_frame.grid_forget()
    dsp_frame.grid_forget()
    tcp_frame.grid_forget()

    # Show the selected page
    if page == "Home":
        home_frame.grid(row=0, column=1, sticky=N)

    elif page == "CPT":
        cpt_frame.grid(row=0, column=1, sticky=N)   

    elif page == "VST":
        vst_frame.grid(row=0, column=1, sticky=N)   

    elif page == "DSP":
        dsp_frame.grid(row=0, column=1, sticky=N)   
    
    elif page == "TCP":
        tcp_frame.grid(row=0, column=1, sticky=N)   

# Define the icons to be shown and resize it
home = ImageTk.PhotoImage(Image.open('.\\gui_images\\home.png').resize((40,40)), Image.Resampling.LANCZOS)
cpt = ImageTk.PhotoImage(Image.open('.\\gui_images\\cpt.png').resize((40,40)), Image.Resampling.LANCZOS)
vst = ImageTk.PhotoImage(Image.open('.\\gui_images\\vst.png').resize((40,40)), Image.Resampling.LANCZOS)
dsp = ImageTk.PhotoImage(Image.open('.\\gui_images\\dsp.png').resize((40,40)), Image.Resampling.LANCZOS)
tcp = ImageTk.PhotoImage(Image.open('.\\gui_images\\tcp.png').resize((40,40)), Image.Resampling.LANCZOS)
imu = ImageTk.PhotoImage(Image.open('.\\gui_images\\imu.png').resize((40,40)), Image.Resampling.LANCZOS)
folders = ImageTk.PhotoImage(Image.open('.\\gui_images\\data_folder.png').resize((40,40)), Image.Resampling.LANCZOS)

root.update() # For the width to get updated
frame = Frame(root,bg='orange',width=50,height=root.winfo_height())
frame.grid(row=0,column=0) 

# Make the buttons with the icons to be shown
home_b = Button(frame,image=home,bg='orange',relief='flat', command=lambda: show_page("Home"))
cpt_b = Button(frame,image=cpt,bg='orange',relief='flat',   command=lambda: show_page("CPT"))
vst_b = Button(frame,image=vst,bg='orange',relief='flat',   command=lambda: show_page("VST"))
dsp_b = Button(frame,image=dsp,bg='orange',relief='flat',   command=lambda: show_page("DSP"))
tcp_b = Button(frame,image=tcp,bg='orange',relief='flat',   command=lambda: show_page("TCP"))
imu_b = Button(frame,image=imu,bg='orange',relief='flat',   command=lambda: show_page("IMU"))

# Put them on the frame
home_b.grid(row=0,column=0, pady=15)
cpt_b.grid(row=1,column=0, pady=15)
vst_b.grid(row=2,column=0, pady=15)
dsp_b.grid(row=3,column=0, pady=15)
tcp_b.grid(row=4,column=0, pady=15)
imu_b.grid(row=5,column=0, pady=15)

# Bind to the frame, if entered or left
frame.bind('<Enter>',lambda e: expand())
frame.bind('<Leave>',lambda e: contract())

# So that it does not depend on the widgets inside the frame
frame.grid_propagate(False)

# ========================================================================
actuator = serial.Serial('COM20', baudrate=9600, timeout=1)
# stepper = serial.Serial('COM6', baudrate=38400, bytesize=8, parity='N', stopbits=1, xonxoff=False)

def go_to():
    # stepper.write('@0A200\r'.encode())
    # stepper.write('@0B200\r'.encode())
    # stepper.write('@0M1000\r'.encode())
    # stepper.write('@0P5000\r'.encode())
    # stepper.write('@0G\r'.encode())   
    # stepper.write('@0F\r'.encode())   
    print('Rotating forward...')
def reset():
    # stepper.write('@0P0\r'.encode())
    # stepper.write('@0G\r'.encode())
    # stepper.write('@0F\r'.encode())
    print('Resetting position...')
    
def digitalWrite(command):
    actuator.write(command.encode())
    print('Command sent:', command)

csv_list = []
torque_csv = []
dsp_idf = []
tcp_csv = []

# Directory adjusts to any PC
current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Data output directories for each component
cpt_dir = f'.\\data_output\\cpt\\{todays_date}'
vst_dir = f'.\\data_output\\vst\\{todays_date}'
dsp_dir = f'.\\data_output\\dsp\\{todays_date}'
tcp_dir = f'.\\data_output\\tcp\\{todays_date}'

strain_data = []
entry_nums = []

lc_running = False
ts_running = False
dsp_running = False
tcp_running = False

dsp_connected = False

# Time elapsed (at the end of this method) will be the total 
total_time = 0
sample_rate = 1655

acquisition_duration = 0
vst_duration = 45

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
    elif device is curr_log4:
        device.config(text=tcp_csv[0], background='#15eb80')

def newton_update():
    curr_newt.config(text='{:.3f}'.format(max(strain_data)), background='white')
    
# Load Cell Read       
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
        ai_task.ai_channels.add_ai_bridge_chan("cDAQ1Mod1/ai0")
        ai_task.ai_channels.ai_bridge_units = BridgePhysicalUnits.NEWTONS
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 2000

        # Start the task
        
        # CLEAR/RESET OLD DATA EVERY NEW RUN TO PREVENT INTERFERANCE!
        entry_nums.clear()
        r_count = 1
        
        ai_task.start()
        digitalWrite('W')
        lc_running = True
        switch_true(load_running)
        start_time = dt.datetime.now()
        
        with open(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', 'a', newline='') as file:

            writer = csv.writer(file)
            
            for i in range(cpt_samples):
                strain = ai_task.read()     # Read current value
                true_strain = strain * -1   # Inversion (raw readings come negative for some)
                newton = (strain * (-96960)) - 1.12 # -96960 gain, 1.12 zero offset
                cdepth = r_count / 7712     # About 7705 data points per centimeter at 3 Volts

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
            file.close()
        
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        lc_running = False
        switch_false(load_running)
        newton_update()
        digitalWrite('s')
        print('CPT Run Completed!')
        tk.messagebox.showinfo("CPT Run Completed", "Total time elapsed: {:.3f} seconds".format(total_time))

# Torque Sensor Read
def read_torque_sensor():
    global total_time
    global ts_running
    
    vst_samples = int(sample_rate * vst_duration)
    
    with nidaqmx.Task() as ai_task:
         
        # Setup the NI cDAQ-9174 + DAQ 9237 module
        # Specify the DAQ port (find using NI-MAX)
        # Then choose the units + sample rate + acquisition type
        ai_task.ai_channels.add_ai_bridge_chan("cDAQ1Mod1/ai1")
        ai_task.ai_channels.ai_bridge_units = BridgePhysicalUnits.INCH_POUNDS
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 5000
        
        ai_task.start()
        go_to()
        ts_running = True
        switch_true(torque_running)
        start_time = dt.datetime.now()
        
        with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'a', newline='') as file:
            writer = csv.writer(file)
            for i in range(vst_samples):
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
                
                # Write current value to CSV
                # Real-time so that the GUI plot can keep up
                writer.writerow([rounded_seconds, lb_inch, true_torque])
            file.close()
                
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        ts_running = False
        switch_false(torque_running)
        print('VST Run Completed!')
        tk.messagebox.showinfo("VST Run Completed", "Total time elapsed: {:.3f} seconds\n NOW RESET THE MOTOR POSITION!".format(total_time))

# Temperature Read
def read_tcp():
    global tcp_running
    
    with nidaqmx.Task() as ai_task:
        ai_task.ai_channels.add_ai_rtd_chan(physical_channel='cDAQ1Mod2/ai0', min_val=0.0, max_val=100.0, units=TemperatureUnits.DEG_F, rtd_type=RTDType.PT_3750, resistance_config=ResistanceConfiguration.THREE_WIRE, current_excit_source=ExcitationSource.INTERNAL, current_excit_val=1.0e-3, r_0=100.0)
        
        ai_task.start()
        tcp_running = True
        switch_true(temp_running)
        start_time = dt.datetime.now()
        
        with open(f'.\\data_output\\tcp\\{todays_date}\\{tcp_csv[0]}', 'a', newline='') as file:
            print(tcp_csv[0])
            writer = csv.writer(file)

            while tcp_running:
                temp = ai_task.read()     # Read current value
                true_temp = temp * -1   # Inversion (raw readings come negative for some reason)
                temp_f = (temp * (-42960)) - 11.0     # (raw readings * gain) minus offset

                now = dt.datetime.now()
                
                # Calculate current time, starting from 0 seconds
                # Then store in global timestamps list for plotting
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)
                
                writer.writerow([rounded_seconds, true_temp])
                file.flush()
                
            file.close()    
                       
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        print('TCP Run Completed!')
        tk.messagebox.showinfo("TCP Run Completed", "Total time elapsed: {:.3f} seconds".format(total_time))
            
def stop_tcp():
    global tcp_running
    tcp_running = False
    switch_false(temp_running)
    
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
        tk.messagebox.showinfo("Error", 'Please open IviumSoft if you want to connect to a device!')
    elif status == 1:
        dsp_connected = True
        switch_true(dsp_status)
        device_serial = (Core.IV_readSN())
        device_update(dsp_device, device_serial[1])
    elif status == 3:
        tk.messagebox.showinfo("Error", 'No device detected!')

# Start the scan operation using the selected preset method
# TEMPORARY: currently statically set to 0.01V method
def scan_op(method):
    global dsp_running
    
    # Merge ivium.py directory + dsp_settings folder + chosen settings
    dsp_methods = os.path.join(current_directory, 'dsp_settings', method)
    
    Core.IV_readmethod(dsp_methods)
    
    dsp_running = True
    switch_true(dsp_runstatus)
    Core.IV_startmethod(dsp_methods)
    time.sleep(175)
    dsp_running = False
    tk.messagebox.showinfo("DSP Scan Completed!", 'Successfully completed! Your .idf file is ready to save!')
    switch_false(dsp_runstatus)
    print('DSP Run Completed!')

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

fig1.text(0.01, 0.97, f"Plotted: {todays_date}", ha='left', va='top', fontsize=10.5)
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

fig2.text(0.01, 0.97, f"Plotted: {todays_date}", ha='left', va='top', fontsize=10.5)

#endregion

# Temperature Sensor
#region
fig3 = Figure(figsize=(4.5,4.5), dpi=100)
fig3.subplots_adjust(left=0.19, bottom=0.15)
temp_sensor = fig3.add_subplot(111)

# Labels Setup
tcp_line, = temp_sensor.plot([], [], linestyle='solid', linewidth='2', color='purple')
temp_sensor.set_title('Thermal Conductivity Probe', weight='bold')  
temp_sensor.set_xlabel('Time Elapsed (seconds)')
temp_sensor.set_ylabel('Degrees (Fahrenheit)')
temp_sensor.grid()

fig3.text(0.01, 0.97, f"Plotted: {todays_date}", ha='left', va='top', fontsize=10.5)
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

# Temperature Sensor Animate Function  
def animate_tcp(i):
    global tcp_running
    if tcp_csv and tcp_running is True:
        data = pd.read_csv(f'.\\data_output\\tcp\\{todays_date}\\{tcp_csv[0]}', sep=",")
        x = data['Timestamp (seconds)'] 
        y = data['Temperature [Fahrenheit]']                             
        
        tcp_line.set_data(x,y)
        temp_sensor.relim()
        temp_sensor.autoscale_view()

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

# Get Torque CSV log name
def get_torque_csv():
    global torque_csv
    global vst_dir
    input = torque_entry.get()
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(torque_csv) == 0:
        torque_csv.append(input)
        print("Torque CSV set to:", input)
    else:
        torque_csv[0] = input
        print("Torque CSV replaced with:", input)
    log_update(curr_log2)
    
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(vst_dir):
        os.makedirs(vst_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Torque [Pound-inches]", "Torque [Raw Reading]"])
        file.close()

# Get DSP IDF log name
def get_dsp_idf():
    global dsp_idf
    input = dsp_entry.get()
    
    # If the list of idfs is empty, append
    # Otherwise, replace the current stored idf
    if len(dsp_idf) == 0:
        dsp_idf.append(input)
        print("DSP IDF set to:", input)
    else:
        dsp_idf[0] = input
        print("DSP IDF replaced with:", input)
    log_update(curr_log3)
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(dsp_dir):
        os.makedirs(dsp_dir)

# Get TCP CSV log name
def get_tcp_csv():
    global tcp_csv
    global tcp_dir
    input = tcp_entry.get()
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(tcp_csv) == 0:
        tcp_csv.append(input)
        print("TCP CSV set to:", input)
    else:
        tcp_csv[0] = input
        print("TCP CSV replaced with:", input)
    log_update(curr_log4)
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(tcp_dir):
        os.makedirs(tcp_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\tcp\\{todays_date}\\{tcp_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Temperature [Fahrenheit]"])
        file.close()
        
# ========================
# Set Durations + Depths
# ========================

# Set/Change VST Rotation Duration
def set_vst_dur():
    global vst_duration
    input = ttime_entry.get()
    if '.' in input:
        tk.messagebox.showinfo("Error", 'Please enter a whole number!')
    else:  
        vst_duration = int(input)
        rot_dur.config(text='{:.2f}'.format(vst_duration))
        print("VST Duration set to:", vst_duration)

# =========================================
# Load Cell + Torque Sensor Run Operations
# =========================================

# Run all load cell operations (read, log, plot)    
def load_cell_run():
    if acquisition_duration == 0:
        tk.messagebox.showinfo("Error", "Please select an actuator depth first!")
        return
    thread_cpt = Thread(target=read_load_cell)
    thread_cpt.start()
    
def torque_sensor_run():
    thread_vst = Thread(target=read_torque_sensor) 
    thread_vst.start()
    
def tcp_run():
    thread_tcp = Thread(target=read_tcp) 
    thread_tcp.start()
    
# ===================
#       Frames
# ===================

# Homepage
#region
jpl_logo = Image.open('.\\gui_images\\jpl_logo_resized.png')
jpl_img = ImageTk.PhotoImage(jpl_logo)
label1 = tk.Label(home_frame,image=jpl_img)
label1.image = jpl_img
label1.grid(row=0, column=0, padx=5, pady=5, sticky=NW)

# Title
main_title = tk.Label(home_frame, text="SPARTA Test Bench Home Page", font=("Arial", 18))
main_title.grid(row=1, column=0, padx=5, pady=5, sticky=NW)  # Update column to 0

author = tk.Label(home_frame, text="Author: Matthew Duong (US 3223 Affiliate)", font=("Arial", 14))
author.grid(row=2, column=0, padx=5, pady=5, sticky=NW)

git_link = tk.Label(home_frame, text='Github Page', font=('Helveticaitalic', 15), fg="blue", cursor="hand2")
git_link.grid(row=3, column=0, padx=5, pady=5, sticky=NW)
git_link.bind("<Button-1>", lambda x: open_url("https://github.com/MattoScientisuto/SPARTA-TestBench"))

cpt_var = tk.StringVar()
vst_var = tk.StringVar()
dsp_var = tk.StringVar()
tcp_var = tk.StringVar()

#endregion

# CPT page
#region
cpt_test = tk.Label(cpt_frame, text='Cone Penetrator', font=("Arial", 18)) 
cpt_test.grid(row=0,column=0, padx=5, pady=6)

set_csv = tk.Label(cpt_frame, text="Set load log name (include .csv): ", font=("Arial", 10)).grid(row=1, column=0, padx=3, pady=3)
entry = tk.Entry(cpt_frame, textvariable=cpt_var)
entry.grid(row=1, column=1, padx=3, pady=3, sticky=W)

dep_var = tk.StringVar()
def update_depth(depth):
    global acquisition_duration
    selected = depth
    if selected == '5 cm':
        acquisition_duration = 23.47 #23.42
    elif selected == '6 cm':
        acquisition_duration = 28.04
    elif selected == '7 cm':
        acquisition_duration = 32.64
    elif selected == '8 cm':
        acquisition_duration = 37.38
    elif selected == '9 cm':
        acquisition_duration = 41.98
    elif selected == '10 cm':
        acquisition_duration = 46.64
    print(f'Selected {selected} actuator depth!')   
dep_options = ['5 cm', '6 cm', '7 cm', '8 cm', '9 cm', '10 cm']
depth_text = tk.Label(cpt_frame, text="Select depth (cm): ", font=("Arial", 10)).grid(row=2, column=0, padx=3, pady=6)
depth_dropdown = tk.OptionMenu(cpt_frame, dep_var, *dep_options, command=update_depth)
depth_dropdown.grid(row=2, column=1, pady=6, sticky=W)

csv_button = tk.Button(cpt_frame, text="Set Name", command=get_csv)
csv_button.grid(row=1, column=2, padx=3, pady=3, sticky=W)

run_button = tk.Button(cpt_frame, text="Run Cone Penetrator", command=load_cell_run)
run_button.grid(row=2, column=2, padx=3, pady=3, sticky=W)

log1 = tk.Label(cpt_frame, text="Logging to: ", font=("Arial", 10)).grid(row=4, column=0)
curr_log1 = tk.Label(cpt_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log1.grid(row=4, column=1, sticky=W, pady=2)

running1 = tk.Label(cpt_frame, text="Currently Running: ", font=("Arial Bold", 10)).grid(row=5, column=0, pady=2)
load_running = tk.Label(cpt_frame, text=str(lc_running), font=("Arial", 14), background='#f05666', relief='groove')
load_running.grid(row=5, column=1, sticky=W, pady=2)
act_estop = tk.Button(cpt_frame, text="Emergency Stop Actuator", command=lambda: digitalWrite('s'))
act_estop.grid(row=3, column=2, sticky=W)

# depth = tk.Label(cpt_frame, text="Current Depth (cm): ", font=("Arial Bold", 10)).grid(row=5, column=0, pady=2)
# curr_depth = tk.Label(cpt_frame, text='0.00', font=("Arial", 14), background='white', relief='groove')
# curr_depth.grid(row=5, column=1, sticky=W, pady=2)
act_reset = tk.Button(cpt_frame, text="Reset Actuator Position", command=lambda: digitalWrite('C'))
act_reset.grid(row=5, column=2, sticky=tk.W)

newt = tk.Label(cpt_frame, text="Greatest Force (Newton): ", font=("Arial Bold", 10)).grid(row=6, column=0, pady=2)
curr_newt = tk.Label(cpt_frame, text='0.00', font=("Arial", 14), background='#e0e0e0', relief='ridge')
curr_newt.grid(row=6, column=1, sticky=W, pady=2)

cpt_folder = tk.Button(cpt_frame, image=folders, command=lambda:open_folder('.\\data_output\\cpt'))
cpt_folder.grid(row=6, column=2)

#endregion

# VST page
#region

vst_test = tk.Label(vst_frame, text='Vane Shear Tester', font=("Arial", 18)) 
vst_test.grid(row=0,column=0, padx=5, pady=6)

set_tcsv = tk.Label(vst_frame, text="Set torque log name (include .csv):", font=("Arial", 10)).grid(row=1, column=0, padx=3, pady=3)
torque_entry = tk.Entry(vst_frame, textvariable=vst_var)
torque_entry.grid(row=1, column=1, padx=3, pady=3, sticky=W)

vst_dur = tk.Label(vst_frame, text="Set rotation duration (seconds):", font=("Arial", 10)).grid(row=2, column=0, padx=3, pady=3)
ttime_entry = tk.Entry(vst_frame)
ttime_entry.grid(row=2, column=1, padx=3, pady=3, sticky=W)

csv_torque_button = tk.Button(vst_frame, text="Set Name", command=get_torque_csv)
csv_torque_button.grid(row=1, column=2, padx=3, pady=3, sticky=W)

ttime_set = tk.Button(vst_frame, text="Set Duration", command=set_vst_dur)
ttime_set.grid(row=2, column=2, padx=3, pady=3, sticky=W)

run_torque_button = tk.Button(vst_frame, text="Run Vane Shear", command=torque_sensor_run)
run_torque_button.grid(row=3, column=2, padx=3, pady=3, sticky=W)

log2 = tk.Label(vst_frame, text="Logging to: ", font=("Arial", 10)).grid(row=4, column=0)
curr_log2 = tk.Label(vst_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log2.grid(row=4, column=1, sticky=W, pady=2)

rot_dial = tk.Label(vst_frame, text="Rotation duration (seconds): ", font=("Arial", 10)).grid(row=5, column=0)
rot_dur = tk.Label(vst_frame, text='{:.2f}'.format(vst_duration), font=("Arial", 14), background='#15eb80', relief='groove')
rot_dur.grid(row=5, column=1, sticky=W, pady=2)

reset_pos = tk.Button(vst_frame, text='Reset Motor Position', command=reset)
reset_pos.grid(row=5, column=2, sticky=W)

running2 = tk.Label(vst_frame, text="Currently Running: ", font=("Arial Bold", 10)).grid(row=6, column=0, pady=2)
torque_running = tk.Label(vst_frame, text=str(lc_running), font=("Arial", 14), background='#f05666', relief='groove')
torque_running.grid(row=6, column=1, sticky=W, pady=2)

vst_folder = tk.Button(vst_frame, image=folders, command=lambda:open_folder('.\\data_output\\vst'))
vst_folder.grid(row=6, column=2)

#endregion

# DSP page
#region

dsp_test = tk.Label(dsp_frame, text='Dielectric Spectrometer', font=("Arial", 18)) 
dsp_test.grid(row=0,column=0, padx=5, pady=6)

dsp_connection = tk.Label(dsp_frame, text="Connected to Ivium: ", font=("Arial Bold", 10)).grid(row=1, column=0, pady=2)
dsp_status = tk.Label(dsp_frame, text=str(dsp_connected), font=("Arial", 14), background='#f05666', relief='groove')
dsp_status.grid(row=1, column=1, sticky=W, pady=2)
dsp_connect = tk.Button(dsp_frame, text="Connect to DSP", command=connect_dsp)
dsp_connect.grid(row=1, column=2, padx=5, pady=5)

dsp_device_status = tk.Label(dsp_frame, text="Device Serial: ", font=("Arial Bold", 10)).grid(row=2, column=0, pady=2)
dsp_device = tk.Label(dsp_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
dsp_device.grid(row=2, column=1, sticky=W, pady=2)

set_didf = tk.Label(dsp_frame, text="Set DSP log name (include .idf):", font=("Arial", 10)).grid(row=3, column=0, padx=3, pady=10)
dsp_entry = tk.Entry(dsp_frame, textvariable=dsp_var)
dsp_entry.grid(row=3, column=1, pady=5, sticky=W)
dsp_torque_button = tk.Button(dsp_frame, text="Set Name", command=get_dsp_idf)
dsp_torque_button.grid(row=3, column=2, padx=5, pady=5)

water_instr = tk.Label(dsp_frame, text="For < 1.0% water: 0.5V Scan\nFor >= 1.0% water: 0.01V Scan", font=("Arial", 12), foreground='blue')
water_instr.grid(row=4, column=0, pady=10, padx=8, sticky=E)

log3 = tk.Label(dsp_frame, text="Logging to: ", font=("Arial", 10)).grid(row=5, column=0)
curr_log3 = tk.Label(dsp_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log3.grid(row=5, column=1, sticky=W, pady=2)
dsp_scan = tk.Button(dsp_frame, text="Run 0.01V Scan", command=lambda:scan_op(dsp_001method))
dsp_scan.grid(row=5, column=2, padx=5, pady=5, sticky=N)
dsp_scan2 = tk.Button(dsp_frame, text="Run 0.5V Scan", command=lambda:scan_op(dsp_05method))
dsp_scan2.grid(row=6, column=2, padx=5, pady=5, sticky=N)

dsp_runtstat = tk.Label(dsp_frame, text='Currently running:', font=("Arial Bold", 10)).grid(row=7, column=0, pady=2)
dsp_runstatus = tk.Label(dsp_frame, text=str(dsp_running), font=("Arial", 14), background='#f05666', relief='groove')
dsp_runstatus.grid(row=7, column=1, sticky=W, pady=2)

dsp_readysave = tk.Label(dsp_frame, text='Ready to save:', font=("Arial Bold", 10)).grid(row=8, column=0, pady=2)
dsp_savestat = tk.Label(dsp_frame, text='False', font=("Arial", 14), background='#f05666', relief='groove')
dsp_savestat.grid(row=8, column=1, sticky=W, pady=2)
dsp_saveidf = tk.Button(dsp_frame, text="Save .idf File", command=save_idf)
dsp_saveidf.grid(row=8, column=2, padx=5, pady=5, sticky=N)

dsp_folder = tk.Button(dsp_frame, image=folders, command=lambda:open_folder('.\\data_output\\dsp'))
dsp_folder.grid(row=9, column=2, pady=10)

#endregion

# TCP page
#region
tcp_test = tk.Label(tcp_frame, text='Thermal Conductivity Probe', font=("Arial", 18)) 
tcp_test.grid(row=0,column=0, padx=5, pady=6)

set_tcp_csv = tk.Label(tcp_frame, text="Set TCP log name (include .csv):", font=("Arial", 10)).grid(row=1, column=0, padx=3, pady=3)
tcp_entry = tk.Entry(tcp_frame)
tcp_entry.grid(row=1, column=1, padx=3, pady=3, sticky=W)
csv_tcp_button = tk.Button(tcp_frame, text="Set Name", command=get_tcp_csv)
csv_tcp_button.grid(row=1, column=2, padx=3, pady=3, sticky=W)

run_tcp_button = tk.Button(tcp_frame, text="Run Temperature Sensor", command=tcp_run)
run_tcp_button.grid(row=2, column=2, padx=3, pady=3, sticky=W)

log4 = tk.Label(tcp_frame, text="Logging to: ", font=("Arial", 10)).grid(row=3, column=0)
curr_log4 = tk.Label(tcp_frame, text='N/A', font=("Arial", 14), background='#f05666', relief='groove')
curr_log4.grid(row=3, column=1, sticky=W, pady=2)

running4 = tk.Label(tcp_frame, text="Currently Running: ", font=("Arial Bold", 10)).grid(row=4, column=0, pady=2)
temp_running = tk.Label(tcp_frame, text=str(tcp_running), font=("Arial", 14), background='#f05666', relief='groove')
temp_running.grid(row=4, column=1, sticky=W, pady=2)

stop_tcp_button = tk.Button(tcp_frame, text="Stop Temperature Sensor", command=stop_tcp)
stop_tcp_button.grid(row=4, column=2, padx=3, pady=3, sticky=W)

tcp_folder = tk.Button(tcp_frame, image=folders, command=lambda:open_folder('.\\data_output\\tcp'))
tcp_folder.grid(row=5, column=2)


#endregion

# =======================
# Plots for every page
# =======================
#region
canvas = FigureCanvasTkAgg(fig1, master=cpt_frame)
canvas.get_tk_widget().grid(row=7, column=0, columnspan=3, padx=30, pady=15)
canvas.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE)

canvas2 = FigureCanvasTkAgg(fig2, master=vst_frame)
canvas2.get_tk_widget().grid(row=7, column=0, columnspan=3, padx=30, pady=15)
canvas2.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE)

canvas3 = FigureCanvasTkAgg(fig3, master=tcp_frame)
canvas3.get_tk_widget().grid(row=6, column=0, columnspan=3, padx=30, pady=15)
canvas3.get_tk_widget().config(borderwidth=2, relief=tk.GROOVE) 
#endregion

ani = FuncAnimation(fig1, animate_load_cell, interval=900, cache_frame_data=False)
ani2 = FuncAnimation(fig2, animate_torque_sensor, interval=900, cache_frame_data=False)
ani3 = FuncAnimation(fig3, animate_tcp, interval=900, cache_frame_data=False)
plt.show()

root.mainloop()