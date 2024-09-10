# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA 
# Zero Gravity: Sensors and Data Acquisition 

# Created: September 3rd, 2024
# Last Updated: September 5th, 2024
# ============================================ #

from DateTimeFetching import *
from LinearMotor import *
from RotateMotor import *

import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits, ExcitationSource, ResistanceConfiguration
from nidaqmx.constants import AcquisitionType, TerminalConfiguration, TorqueUnits, BridgeConfiguration, BridgeElectricalUnits, AcquisitionType, ForceUnits

import time
from datetime import date, datetime
import datetime as dt
import os
import sys
from threading import Thread

import csv
import pandas as pd

sample_rate = 1655

todays_date = date.today().strftime("%m-%d-%Y")
cpt_csv = []
vst_csv = []
cpt_dir = f'C:\\zero_gravity_output\\data_output\\cpt\\{todays_date}\\'
vst_dir = f'C:\\zero_gravity_output\\data_output\\vst\\{todays_date}\\'

r_count = 1

# ==========================
# Load Cell Operations
# ==========================

def get_cpt_csv():

    global cpt_csv
    global cpt_dir

    curr_time = datetime.now().strftime("%H-%M-%S")
    input = f'ZeroG_CPT[{todays_date}][{curr_time}]' '.csv'
    
    cpt_csv.append(input)
    print(f"[{get_timestamp()}] CPT CSV set to:", input)
    sys.stdout.flush()

    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(cpt_dir):
        os.makedirs(cpt_dir)
    
    # Create the csv file and write the column titles
    with open(f'C:\\zero_gravity_output\\data_output\\cpt\\{todays_date}\\{cpt_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Depth [cm]", "Force [Pounds/Raw]"])
        file.close()


def read_load_cell():
    
    global total_time
    global r_count
    
    cpt_samples = int(sample_rate * actuator_duration)
    
    with nidaqmx.Task() as ai_task:
         
        # Setup the NI cDAQ-9174 + DAQ 9237 module
        # Specify the DAQ port (find using NI-MAX)
        # Then choose the units + sample rate + acquisition type
        ai_task.ai_channels.add_ai_force_bridge_two_point_lin_chan("cDAQ2Mod1/ai0", units=ForceUnits.POUNDS, bridge_config=BridgeConfiguration.FULL_BRIDGE, 
                                                                    voltage_excit_source=ExcitationSource.INTERNAL, voltage_excit_val=10.0, nominal_bridge_resistance=350.0, 
                                                                    physical_units=BridgePhysicalUnits.POUNDS)
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 5000

        # Start the task
        
        ai_task.start()
        
        digitalWrite(linear_actuator, 'W5000')
        
        start_time = dt.datetime.now()

        with open(f'C:\\zero_gravity_output\\data_output\\cpt\\{todays_date}\\{cpt_csv[0]}', 'a', newline='') as file:

            writer = csv.writer(file)
            last_timestamp = 0
            
            for i in range(cpt_samples):
                strain = ai_task.read()     # Read current value
                true_strain = strain * -1   # Inversion
                cdepth = r_count / 1732     # About 1732 data points per centimeter at 12 Volts

                now = dt.datetime.now()
                
                # Calculate current time, starting from 0 seconds
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)

                continued_timestamp = last_timestamp + rounded_seconds

                r_count+=1
                
                # Write current value to CSV
                writer.writerow([continued_timestamp, cdepth, true_strain])
                
            file.close()
            
        time.sleep(0.1)
        digitalWrite(linear_actuator, 's')

        # Close port safely, prep for re-open and reset
        # needs testing first
        linear_actuator.close()

        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        time_print('CPT Run Completed!')

# ==========================
# Torque Sensor Operations
# ==========================

def get_vst_csv():

    global vst_csv
    global vst_dir
    curr_time = datetime.now().strftime("%H-%M-%S")
    input = f'ZeroG_VST[{todays_date}][{curr_time}]' '.csv'
    
    vst_csv.append(input)
    print(f"[{get_timestamp()}] VST CSV set to:", input)
    sys.stdout.flush()

    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(vst_dir):
        os.makedirs(vst_dir)
    
    # Create the csv file and write the column titles
    with open(f'C:\\zero_gravity_output\\data_output\\vst\\{todays_date}\\{vst_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Torque [Pound-inches/Raw]"])
        file.close()


# Torque Sensor Read
def read_torque_sensor():

    global total_time
    
    vst_samples = int(sample_rate * vst_seconds)
    
    with nidaqmx.Task() as ai_task:
         
        # Setup the NI cDAQ-9174 + DAQ 9237 module
        # Specify the DAQ port (find using NI-MAX)
        # Then choose the units + sample rate + acquisition type
        ai_task.ai_channels.add_ai_torque_bridge_two_point_lin_chan("cDAQ2Mod1/ai1", units=TorqueUnits.INCH_POUNDS, bridge_config=BridgeConfiguration.FULL_BRIDGE, 
                                                                    voltage_excit_source=ExcitationSource.INTERNAL, voltage_excit_val=10.0, nominal_bridge_resistance=350.0, 
                                                                    physical_units=BridgePhysicalUnits.INCH_POUNDS)
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 5000
        
        ai_task.start()
        rotate_forward()
        start_time = dt.datetime.now()
        
        with open(f'C:\\zero_gravity_output\\data_output\\vst\\{todays_date}\\{vst_csv[0]}', 'a', newline='') as file:
            writer = csv.writer(file)
            last_timestamp = 0

            for i in range(vst_samples):
                torque = ai_task.read()     # Read current value
                true_torque = abs(torque)   # Torque should only go up

                now = dt.datetime.now()
                
                # Calculate current time, starting from 0 seconds
                # Then store in global timestamps list for plotting
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)

                continued_timestamp = last_timestamp + rounded_seconds
                
                # Write current value to CSV
                # Real-time so that the GUI plot can keep up
                writer.writerow([continued_timestamp, true_torque])
                
            file.close()

        stepper.close()
        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        time_print('VST Run Completed!')


# ============
# Threads
# ============

def start_cpt_thread():
    print(f'=======================================================\n START POINT CPT : {get_datestamp()} at {get_timestamp()}\n=======================================================')
    get_cpt_csv()
    time.sleep(1)
    thread_cpt = Thread(target=read_load_cell)
    thread_cpt.start()
    return thread_cpt

def start_vst_thread():
    print(f'=======================================================\n START POINT VST : {get_datestamp()} at {get_timestamp()}\n=======================================================')
    speeds_setup()
    get_vst_csv()
    time.sleep(1)
    thread_vst = Thread(target=read_torque_sensor) 
    thread_vst.start()
    return thread_vst


def reset_cpt_thread():

    thread_reset1 = Thread(target=reset_linear_actuator) 
    thread_reset1.start()
    return thread_reset1

def reset_vst_thread():

    thread_reset1 = Thread(target=reset_rotation_motor) 
    thread_reset1.start()
    return thread_reset1

# Resets

def reset_linear_actuator():

    digitalWrite(linear_actuator, 'C')
    time_print('Homing linear actuator...')

def reset_rotation_motor():

    rotate_reset()
    time_print('Homing rotation motor...')