# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin DSP Sequence: Ground Vane Shear

# Created: March 21th, 2024
# Last Updated: March 21th, 2024
# ============================================ #

import os
import csv
import time
from datetime import date, datetime
import datetime as dt
import serial
import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits, ExcitationSource
from nidaqmx.constants import AcquisitionType, TorqueUnits, BridgeConfiguration, AcquisitionType
import sys
from threading import Thread

# sys.stdout = open("console_log_vstflight.txt", "a")

# ==================================
# Vane Shear Setup
stepper = serial.Serial('COM3', baudrate=38400, bytesize=8, parity='N', stopbits=1, xonxoff=False)
    
sample_rate = 1600
vst_duration = 15
run_counter = 0
torque_csv = []

current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Data output directories for each component
vst_dir = f'.\\data_output\\vst\\{todays_date}'

todays_time = datetime.now().strftime("%H:%M:%S")
print(f'============================================================================================================\nVST {todays_date} at {todays_time}')
print(f'======================================================\n START POINT OF GROUND VST LOG: {todays_date} at {todays_time}\n======================================================')

# Get Torque CSV log name
def get_torque_csv():
    global torque_csv
    global vst_dir
    curr_time = datetime.now().strftime("%H-%M-%S")
    input = 'VST_' + curr_time + '_' + todays_date + '.csv'
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(torque_csv) == 0:
        torque_csv.append(input)
        print("Torque CSV set to:", input)
    else:
        torque_csv[0] = input
        print("Torque CSV replaced with:", input)
    
    sys.stdout.flush()

    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(vst_dir):
        os.makedirs(vst_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Torque (inch-lb) [Raw Reading]", "Torque (inch-lb) [Absolute Value]"])
        file.close()

def rotate_vst():
    stepper.write(f'@0N{vst_duration * 1500}\r'.encode())
    stepper.write('@0G\r'.encode())   
    stepper.write('@0F\r'.encode())   
    print('Rotating forward...')
    sys.stdout.flush()

def ground_vst():
    global total_time

    vst_samples = int(sample_rate * vst_duration)
    
    with nidaqmx.Task() as ai_task:
         
        ai_task.ai_channels.add_ai_torque_bridge_two_point_lin_chan("Dev1/ai3", units=TorqueUnits.INCH_POUNDS, bridge_config=BridgeConfiguration.FULL_BRIDGE, 
                                                                    voltage_excit_source=ExcitationSource.INTERNAL, voltage_excit_val=10.0, nominal_bridge_resistance=350.0, 
                                                                    physical_units=BridgePhysicalUnits.INCH_POUNDS)
        ai_task.timing.cfg_samp_clk_timing(rate=1600,sample_mode=AcquisitionType.CONTINUOUS)
        
        ai_task.start()
        rotate_vst()
        start_time = dt.datetime.now()
        print(f"VST Start Timestamp: {start_time}")
        sys.stdout.flush()
        with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'a', newline='') as file:
            writer = csv.writer(file)

            for i in range(vst_samples):
                torque = ai_task.read()
                true_torque = abs(torque)

                now = dt.datetime.now()
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)
                
                writer.writerow([rounded_seconds, torque, true_torque])

            end_time = dt.datetime.now() 
            total_time = (end_time - start_time).total_seconds()
            print("Total time elapsed: {:.3f} seconds".format(total_time))
            print(f"VST End Timestamp: {end_time}")
            print('VST Run Completed!\n')
            sys.stdout.flush()
            file.close()
            stepper.close()
            sys.stdout.close()

def torque_sensor_run():
    thread_vst = Thread(target=ground_vst) 
    thread_vst.start()

def go_vst():
    get_torque_csv()
    torque_sensor_run()
    
# ===================================
# Driver Sequence
time_now = dt.datetime.now().strftime("%H:%M:%S")
print(f'\n[{todays_date}, {time_now}] Ground VST batch successfully started!')
sys.stdout.flush()
go_vst()