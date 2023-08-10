# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin Bench Sequence

# Created: August 8th, 2023
# Last Updated: August 9th, 2023
# ============================================ #

import tkinter as tk

import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits

from pyvium import Core
from pyvium import Tools

import os
import sys
import csv

from datetime import date, datetime
import datetime as dt
import time

current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Get CPT CSV log name
def get_csv():
    
    curr_time = datetime.now().strftime("%H-%M-%S")
    input = f'CPT_{todays_date}_{curr_time}.csv'
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(csv_list) == 0:
        csv_list.append(input)
        print("Load CSV set to:", input)
    else:
        csv_list[0] = input
        print("Load CSV set to:", input)
        
    # If today's date doesn't have an output folder yet, make one
    if not os.path.exists(cpt_dir):
        os.makedirs(cpt_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\cpt\\{todays_date}\\{csv_list[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Depth [cm]", "Force [Newtons]", "Force [Raw Reading]"])
        file.close()

# Get Torque CSV log name
def get_torque_csv():
   
    curr_time = datetime.now().strftime("%H-%M-%S")
    input = f'VST_{todays_date}_{curr_time}.csv'
    
    if len(torque_csv) == 0:
        torque_csv.append(input)
        print("Torque CSV set to:", input)
    else:
        torque_csv[0] = input
        print("Torque CSV set to:", input)
   
    if not os.path.exists(vst_dir):
        os.makedirs(vst_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Torque [Pound-inches]", "Torque [Raw Reading]"])
        file.close()

# Get DSP IDF log name
def get_dsp_idf():
    
    curr_time = datetime.now().strftime("%H-%M-%S")
    input = f'DSP_{todays_date}_{curr_time}.idf'
    
    if len(dsp_idf) == 0:
        dsp_idf.append(input)
        print("DSP IDF set to:", input)
    else:
        dsp_idf[0] = input
        print("DSP IDF set to:", input)
    
    if not os.path.exists(dsp_dir):
        os.makedirs(dsp_dir)

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
    Core.IV_connect(1)
    
    status = Core.IV_getdevicestatus()
    print(Core.IV_getdevicestatus())
    if status == -1:
        print('Ivium not opened')
    elif status == 1:
        dsp_connected = True
    elif status == 3:
        print('No device detected')

# Start the scan operation using the selected preset method
# TEMPORARY: currently statically set to 0.01V method
def scan_op():
    Core.IV_readmethod(dsp_methods)  
    Core.IV_startmethod(dsp_methods)

# After the scanning finishes, user can save the data to the output folder
def save_idf():
    if len(dsp_idf) == 0:
        print('No name selected yet')
    else:
        dsp_output = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf[0])
        print(Core.IV_savedata(dsp_output))
        

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

lbs_inches = []
raw_torque = []
torque_timestamps = []

entry_nums = []
r_count = 1

lc_running = False
ts_running = False
dsp_running = False

dsp_connected = False

# Time elapsed (at the end of this method) will be the total 
total_time = 0
sample_rate = 50.0
acquisition_duration = 620 #45 is 28 seconds, 41 is mms and jsc tested 7-12
num_of_samples = int(sample_rate * acquisition_duration)

def full_op():
    global total_time
    global lc_running
    global r_count
    
    get_csv()
    
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
                r_count+=1
                
                # Write current value to CSV
                # Real-time so that the GUI plot can keep up
                writer.writerow([timestamps[i], entry_nums[i], strain_data[i], strain_orig[i]])
            file.close()
                
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        lc_running = False
        print('CPT Run Completed!')
        
    # ============================================
        
    global ts_running
    
    get_torque_csv()
    
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
        start_time = dt.datetime.now()
        
        with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'a', newline='') as file:
            writer = csv.writer(file)
            for i in range(num_of_samples):
                torque = ai_task.read()     # Read current value
                true_torque = torque * -1   # Inversion (raw readings come negative for some reason)
                lb_inch = (torque * (-42960)) - 11.0     # (raw readings * gain) minus offset

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
        print('VST Run Completed!')

    # ============================================
    
    get_dsp_idf()

    connect_dsp()
    scan_op()
    time.sleep(150)
    save_idf()
    print('DSP Sweep Completed!')

# ===================================
# Driver Sequence

full_op()