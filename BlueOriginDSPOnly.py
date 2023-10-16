# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin DSP Sequence

# Created: September 11th, 2023
# Last Updated: October 16th, 2023
# ============================================ #

from pyvium import Core
from pyvium import Tools

import os
import sys
import csv

from datetime import date, datetime
import datetime as dt
import time

import subprocess

dsp_idf = []
dsp_idf2 = []

current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Data output directories for each component
dsp_dir = f'.\\data_output\\dsp\\{todays_date}'


# Get DSP IDF log name
def get_dsp_idf():
    
    # Channel 1
    curr_time = datetime.now().strftime("%H-%M-%S")
    Core.IV_SelectChannel(1)
    serial = (Core.IV_readSN())
    input = f'{serial[1]}_{todays_date}_{curr_time}.idf'
    
    if len(dsp_idf) == 0:
        dsp_idf.append(input)
        print("\n[CHANNEL 1] IDF set to: ", input)
    else:
        dsp_idf[0] = input
        print("\n[CHANNEL 1] IDF replaced with: ", input)
    
    if not os.path.exists(dsp_dir):
        os.makedirs(dsp_dir)
        
    time.sleep(1)
        
    # Channel 2
    curr_time = datetime.now().strftime("%H-%M-%S")
    Core.IV_SelectChannel(2)
    serial2 = (Core.IV_readSN())    
    input2 = f'{serial2[1]}_{todays_date}_{curr_time}.idf'
    
    if len(dsp_idf2) == 0:
        dsp_idf2.append(input2)
        print("[CHANNEL 2] IDF set to: ", input2)
    else:
        dsp_idf2[0] = input2
        print("[CHANNEL 2] IDF replaced with: ", input2)

# EIS230724140245.imf = 0.01V for samples < 1.0% water
# EIS230724135821.imf = 0.5V for samples >= 1.0% water
dsp_001method = 'EIS230724140245.imf'
dsp_05method = 'EIS230724135821.imf'

# Connect to DSP
def connect_dsp():

    # Channel 1 DSP: 
    Core.IV_SelectChannel(1)
    Core.IV_selectdevice=1
    # '1' means to connect
    Core.IV_connect(1)
    
    time.sleep(1)
    
    # Channel 2 DSP:
    Core.IV_SelectChannel(2)
    Core.IV_selectdevice=2
    Core.IV_connect(1)
    
    time.sleep(1)
    
    status = Core.IV_getdevicestatus()
    if status == -1:
        print('Ivium not opened')
    elif status == 3:
        print('No device detected')

# Start the scan operation using the selected preset method
# TEMPORARY: currently statically set to 0.01V method
def scan_op():
    # Merge ivium.py directory + dsp_settings folder + chosen settings
    dsp_methods = os.path.join(current_directory, 'dsp_settings', dsp_001method)
    
    # Channel 1
    Core.IV_SelectChannel(1)
    Core.IV_readmethod(dsp_methods)
    Core.IV_startmethod(dsp_methods)
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f"[CHANNEL 1] Scan started at: {time_now}")
    sys.stdout.flush()
    
    time.sleep(1)
    
    # Channel 2
    dsp_methods2 = os.path.join(current_directory, 'dsp_settings', dsp_05method)
    Core.IV_SelectChannel(2)
    Core.IV_readmethod(dsp_methods2)
    time.sleep(0.5)
    Core.IV_startmethod(dsp_methods2)
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f"[CHANNEL 2] Scan started at: {time_now}")

# After the scanning finishes, user can save the data to the output folder
def save_idf():
    Core.IV_SelectChannel(1)
    dsp_output = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf[0])
    ch1_savelog = Core.IV_savedata(dsp_output)
    print(f'[CHANNEL 1] IDF saved at:\n {ch1_savelog[1]}')
    
    time.sleep(0.5)
    
    Core.IV_SelectChannel(2)
    dsp_output2 = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf2[0])
    ch2_savelog = Core.IV_savedata(dsp_output2)
    print(f'[CHANNEL 2] IDF saved at:\n {ch2_savelog[1]}')

def dsp_wait():
    while True:
        # Channel 1
        Core.IV_SelectChannel(1)
        status = Core.IV_getdevicestatus()
        
        time.sleep(0.5)
        
        # Channel 2
        Core.IV_SelectChannel(2)
        status2 = Core.IV_getdevicestatus()
        
        # Check both if they're done
        # Will only proceed once both are done (subject to change)
        if status == 1 and status2 == 1:
            return status
        
        # Check in 10 second intervals
        time.sleep(10)

def start_ivium():
    # Start IviumSoft.exe
    subprocess.call([r'start_ivium.bat'])
    time.sleep(8)
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'Ivium opened at: {time_now}')

def start_imu():
    subprocess.call([r'start_IMU.bat'])
    time.sleep(10)
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'IMU Executable opened at: {time_now}')

def full_op():

    # Power up ivium and IMU
    # 8 second delay for each to open on time before scanning
    start_ivium()
    # start_imu()

    Core.IV_open()
    time.sleep(0.1)
    
    # Always start on channel 1
    connect_dsp()
    time.sleep(1)
    
    # Data Collection Loop
    while True:
        get_dsp_idf()
        scan_op()
        
        status = dsp_wait()
        print(f'All Devices Statuses: {status}, Idle & ready to restart!')
        
        save_idf()
        time_now = dt.datetime.now().strftime("%H:%M:%S")
        print(f'DSP Sweep on both channels completed at: {time_now}\n\n===')
        time.sleep(1)
        
    Core.IV_close()
    
# ===================================
# Driver Sequence

full_op()