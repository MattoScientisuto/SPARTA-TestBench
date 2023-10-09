# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin DSP Sequence

# Created: September 11th, 2023
# Last Updated: October 9th, 2023
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

current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Get DSP IDF log name
def get_dsp_idf():
    
    curr_time = datetime.now().strftime("%H-%M-%S")
    serial = (Core.IV_readSN())
    input = f'{serial[1]}_{todays_date}_{curr_time}.idf'
    
    if len(dsp_idf) == 0:
        dsp_idf.append(input)
        print(f"\nDSP IDF set to: {input}")
    else:
        dsp_idf[0] = input
        print(f"\nDSP IDF replaced with: {input}")
    
    if not os.path.exists(dsp_dir):
        os.makedirs(dsp_dir)

# EIS230724140245.imf = 0.01V for samples under 1.0% water
# EIS230724135821.imf = 0.5V for samples over 1.0% water
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
    # Core.IV_SelectChannel(2)
    # Core.IV_selectdevice=2
    # Core.IV_connect(1)
    
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
    Core.IV_SelectChannel(1)
    Core.IV_readmethod(dsp_methods)
    Core.IV_startmethod(dsp_methods)
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f"Scan started at: {time_now}")
    sys.stdout.flush()
    time.sleep(1)
    
    # dsp_methods = os.path.join(current_directory, 'dsp_settings', dsp_05method)
    # Core.IV_SelectChannel(2)
    # Core.IV_readmethod(dsp_methods)
    # time.sleep(1)
    # Core.IV_startmethod(dsp_methods)

# After the scanning finishes, user can save the data to the output folder
def save_idf():
    Core.IV_SelectChannel(1)
    dsp_output = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf[0])
    print(Core.IV_savedata(dsp_output))
    
    time.sleep(1)
    
    # print(Core.IV_SelectChannel(2))
    # get_dsp_idf()
    # dsp_output = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf[0])
    # print(Core.IV_savedata(dsp_output))
        

dsp_idf = []

# Directory adjusts to any PC
current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Data output directories for each component
dsp_dir = f'.\\data_output\\dsp\\{todays_date}'

def dsp_wait():
    while True:
        status = Core.IV_getdevicestatus()
        if status == 1:
            return status
        time.sleep(10)

def start_ivium():
    # Start IviumSoft.exe
    subprocess.call([r'start_ivium.bat'])
    time.sleep(5)
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'Ivium started at: {time_now}')

def full_op():

    start_ivium()

    Core.IV_open()
    time.sleep(0.1)
    
    # Always start on channel 1
    Core.IV_SelectChannel(1)
    connect_dsp()
    time.sleep(1)
    
    # Data Collection Loop
    while True:
        get_dsp_idf()
        scan_op()
        
        status = dsp_wait()
        print(f'Device Status: {status}, Device idle & ready')
        
        save_idf()
        time_now = dt.datetime.now().strftime("%H:%M:%S")
        print(f'DSP Sweep Completed at: {time_now}\n')
        time.sleep(1)
        
    Core.IV_close()
    
# ===================================
# Driver Sequence

full_op()