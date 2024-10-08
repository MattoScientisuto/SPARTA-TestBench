# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: DSP Loop

# Created: September 3rd, 2024
# Last Updated: October 8th, 2024
# ============================================ #
import PathSetup
from general_fetching_scripts.DateTimeFetching import *

from pyvium import Core

import os
import sys
import time

import subprocess
import atexit


log_path = f"C:\\zero_gravity_output\\data_output\\dsp\\{get_datestamp()}\\console_log_dspimu.txt"
os.makedirs(os.path.dirname(log_path), exist_ok=True)
sys.stdout = open(log_path, "a")


dsp_idf = []
dsp_dir = f'C:\\zero_gravity_output\\data_output\\dsp\\{get_datestamp()}'
current_directory = os.path.dirname(os.path.abspath(__file__))

# EIS230724140245.imf = 0.01V for samples < 1.0% water
# EIS230724135821.imf = 0.5V for samples >= 1.0% water
dsp_001method = 'EIS230724140245.imf'
dsp_05method = 'EIS230724135821.imf'


# Start IviumSoft.exe
def start_ivium():

    ivium_path = os.path.join(os.path.dirname(__file__), 'start_ivium.bat')

    try:
        subprocess.call([ivium_path])
        print(f'[{get_timestamp()}] Ivium successfully started!')
    except Exception as e:
        print(f'Error starting Ivium: {e}')
    finally:
        sys.stdout.flush()


# Connect to DSP
def connect_dsp():

    # Channel 1 DSP: 
    Core.IV_SelectChannel(1)
    Core.IV_selectdevice(1)
    # '1' means to connect
    Core.IV_connect(1)
    
    time.sleep(3)
    
    status = Core.IV_getdevicestatus()
    if status == -1:
        print('Ivium not opened')
    elif status == 3:
        print('No device detected')


# Get DSP IDF log name
def get_dsp_idf():
    
    # Channel 1
    Core.IV_SelectChannel(1)
    serialjuan = (Core.IV_readSN())
    print(f"[{get_timestamp()}][CHANNEL 1] Device selected: ", serialjuan)
    inputjuan = f'ZeroG_DSP_{serialjuan[1]}_[{get_datestamp()}]_[{get_dashedtime()}].idf'
    
    # If there's no existing IDF names in the array yet, add it
    if len(dsp_idf) == 0:
        dsp_idf.append(inputjuan)
        print(f"[{get_timestamp()}][CHANNEL 1] IDF set to: ", inputjuan)
    # Otherwise, just replace the previous one
    else:
        dsp_idf[0] = inputjuan
        print(f"[{get_timestamp()}][CHANNEL 1] IDF replaced with: ", inputjuan)
    
    if not os.path.exists(dsp_dir):
        os.makedirs(dsp_dir)


# Start the scan operation using the selected preset method
def scan_op():
    # Merge ivium.py directory + dsp_settings folder + chosen settings
    dsp_methods = os.path.join(current_directory, 'dsp_settings', dsp_05method)
    
    # Channel 1
    Core.IV_SelectChannel(1)
    Core.IV_readmethod(dsp_methods)
    Core.IV_startmethod(dsp_methods)

    print(f"[{get_timestamp()}][CHANNEL 1] Scan started at: {get_timestamp()}")
    sys.stdout.flush()
    
    time.sleep(2)


# After the scanning finishes, save the data to the output folder
def save_idf():
    Core.IV_SelectChannel(1)
    dsp_output = os.path.join(f'c:\zero_gravity_output\data_output\dsp\{get_datestamp()}', dsp_idf[0])
    print(f"[{get_timestamp()}][CHANNEL 1] IDF saved: ", Core.IV_savedata(dsp_output))
    sys.stdout.flush()


# Periodically check dsp channel to see if scanning is done
def dsp_wait():

    while True:

        # Channel 1
        Core.IV_SelectChannel(1)
        status = Core.IV_getdevicestatus()
        
        # Check both if they're done
        # Will only proceed once both are done (subject to change)
        if status == 1:
            return status
        
        # Check in 5 second intervals
        time.sleep(5)


if __name__ == "__main__":

    print(f'====================================================\n START POINT OF DSP LOG: {get_datestamp()} at {get_timestamp()}\n====================================================')
    sys.stdout.flush()

    print(f'\n[{get_datestamp()}, {get_timestamp()}] DSP batch successfully started!')

    # Power up Ivium and IMU
    start_ivium()
    time.sleep(3)
    Core.IV_open()
    time.sleep(3)
    
    # Always start on channel 1
    connect_dsp()
    time.sleep(3)
    
    # Data Collection Loop
    while True:
        get_dsp_idf()
        scan_op()
        
        sys.stdout.flush()
        time.sleep(3)
        time_print('Pre-wait DSP check delay ended, start periodically checking DSP Channel 1 for completion!')
        sys.stdout.flush()

        status = dsp_wait()
        time_print(f'All Devices Statuses: {status}, Idle & ready to restart!')
        sys.stdout.flush()

        save_idf()
        time_print(f'DSP Sweep on all channels completed\n\n===\n')
        sys.stdout.flush()
        time.sleep(1)

def exit_handler():
            sys.stdout.close()

atexit.register(exit_handler)