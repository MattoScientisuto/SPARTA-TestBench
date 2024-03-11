# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin DSP Sequence

# Created: September 11th, 2023
# Last Updated: March 11th, 2024
# ============================================ #

# COM25 and 4800 baudrate = IMU
# COM26 and 9600 baudrate = Stepper Motor

from pyvium import Core
from pyvium import Tools

import os
import sys
import csv

from datetime import date, datetime
import datetime as dt
import time

import subprocess
import psutil

import serial
import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits, ExcitationSource
from nidaqmx.constants import AcquisitionType, TorqueUnits, BridgeConfiguration, AcquisitionType
from threading import Thread

sys.stdout = open("console_log_dspimu.txt", "a")

# ==================================
# DSP and IMU

dsp_idf = []
dsp_idf2 = []

current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")
todays_time = datetime.now().strftime("%H:%M:%S")
print(f'====================================================\n START POINT OF DSP LOG: {todays_date} at {todays_time}\n====================================================')

# Data output directories for each component
dsp_dir = f'.\\data_output\\dsp\\{todays_date}'

# Get DSP IDF log name
def get_dsp_idf():
    
    # Channel 1
    curr_time = datetime.now().strftime("%H-%M-%S")
    Core.IV_SelectChannel(1)
    serialjuan = (Core.IV_readSN())
    print("[CHANNEL 1] Device selected: ", serialjuan)
    inputjuan = f'{serialjuan[1]}_{todays_date}_{curr_time}.idf'
    
    # If there's no existing IDF names in the array yet, add it
    if len(dsp_idf) == 0:
        dsp_idf.append(inputjuan)
        print("[CHANNEL 1] IDF set to: ", inputjuan)
    # Otherwise, just replace the previous one
    else:
        dsp_idf[0] = inputjuan
        print("[CHANNEL 1] IDF replaced with: ", inputjuan)
    
    if not os.path.exists(dsp_dir):
        os.makedirs(dsp_dir)


    # Channel 2
    curr_time = datetime.now().strftime("%H-%M-%S")
    Core.IV_SelectChannel(2)
    serial2 = (Core.IV_readSN())    
    print("[CHANNEL 2] Device selected: ", serial2)
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
    
    time.sleep(3)
    
    # Channel 2 DSP:
    Core.IV_SelectChannel(2)
    Core.IV_selectdevice=2
    Core.IV_connect(1)
    
    time.sleep(3)
    
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
    
    time.sleep(2)
    
    # Channel 2
    dsp_methods2 = os.path.join(current_directory, 'dsp_settings', dsp_001method)
    Core.IV_SelectChannel(2)
    Core.IV_readmethod(dsp_methods2)
    time.sleep(1)
    Core.IV_startmethod(dsp_methods2)
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f"[CHANNEL 2] Scan started at: {time_now}")

# After the scanning finishes, user can save the data to the output folder
def save_idf():
    Core.IV_SelectChannel(1)
    dsp_output = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf[0])
    print("[CHANNEL 1] IDF saved: ", Core.IV_savedata(dsp_output))
    
    time.sleep(1)
    
    Core.IV_SelectChannel(2)
    dsp_output2 = os.path.join(current_directory, 'data_output', 'dsp', todays_date, dsp_idf2[0])
    print("[CHANNEL 2] IDF saved: ", Core.IV_savedata(dsp_output2))

# Check if IMU LabView program is open yet
def dsp_wait():
    while True:
        # Channel 1
        Core.IV_SelectChannel(1)
        status = Core.IV_getdevicestatus()
        
        time.sleep(1)
        
        # Channel 2
        Core.IV_SelectChannel(2)
        status2 = Core.IV_getdevicestatus()
        
        # Check both if they're done
        # Will only proceed once both are done (subject to change)
        if status == 1 and status2 == 1:
            return status
        
        # Check in 10 second intervals
        time.sleep(10)
# Check if IviumSoft is open yet
def ivium_wait():
    while True:
        ivium_status = "IviumSoft.exe" in (i.name() for i in psutil.process_iter()) 
        
        if ivium_status == True:
            time.sleep(10)
            return ivium_status
            
        time_now = dt.datetime.now().strftime("%H:%M:%S")
        print(f'Ivium still starting up at: {time_now}\nCheck again in 10 seconds...')
        time.sleep(10)
        
# Check if IMU LabView program is open
def imu_wait():
    while True:
        imu_status = "IMU_COM25Ver2.exe" in (i.name() for i in psutil.process_iter()) 
        
        if imu_status == True:
            time.sleep(5)
            return imu_status
            
        time_now = dt.datetime.now().strftime("%H:%M:%S")
        print(f'IMU still starting up at: {time_now}\nCheck again in 10 seconds...')
        time.sleep(10)

# Start IviumSoft.exe
def start_ivium():
    ivium_path = os.path.join(os.path.dirname(__file__), 'start_ivium.bat')
    subprocess.call([ivium_path])
    ivium_wait()
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'Ivium successfully started at: {time_now}')
# Start IMU VI
def start_imu():  
    imu_path = os.path.join(os.path.dirname(__file__), 'start_IMU.bat')
    subprocess.call([imu_path])
    imu_wait()
    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'IMU Executable successfully started at: {time_now}\n')

def full_op():

    time_now = dt.datetime.now().strftime("%H:%M:%S")
    print(f'\n[{todays_date}, {time_now}] Main DSP & IMU batch successfully started!')

    # Power up Ivium and IMU
    start_ivium()
    # start_imu()

    Core.IV_open()
    time.sleep(1)
    
    # Always start on channel 1
    connect_dsp()
    time.sleep(1)
    
    # Data Collection Loop
    while True:
        get_dsp_idf()
        scan_op()
        
        print('Pre-wait DSP check 12-second-delay started')
        time.sleep(12)
        print('Pre-wait DSP check delay ended, start periodically checking DSP Channels 1 and 2 for completion!')

        status = dsp_wait()
        print(f'All Devices Statuses: {status}, Idle & ready to restart!')
        
        save_idf()
        time_now = dt.datetime.now().strftime("%H:%M:%S")
        print(f'DSP Sweep on both channels completed at: {time_now}\n\n===\n')
        time.sleep(1)
        
    Core.IV_close()
    
# ===================================
# Driver Sequence

full_op()