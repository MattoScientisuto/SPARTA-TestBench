# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA Test Bench 
# Blue Origin DSP Sequence: Vane Shear Only

# Created: February 16th, 2024
# Last Updated: February 16th, 2024
# ============================================ #

import os
import csv
from datetime import date, datetime
import datetime as dt
import serial
import nidaqmx
from nidaqmx.constants import BridgePhysicalUnits, ExcitationSource
from nidaqmx.constants import AcquisitionType, TorqueUnits, BridgeConfiguration, AcquisitionType
from threading import Thread

# ==================================
# Vane Shear Setup
stepper = serial.Serial('COM26', baudrate=38400, bytesize=8, parity='N', stopbits=1, xonxoff=False)
def open_stepper_port():
    stepper.open()
    
sample_rate = 1655
vst_duration = 15
torque_csv = []

current_directory = os.path.dirname(os.path.abspath(__file__))
todays_date = date.today().strftime("%m-%d-%Y")

# Data output directories for each component
vst_dir = f'.\\data_output\\vst\\{todays_date}'

# Get Torque CSV log name
def get_torque_csv():
    global torque_csv
    global vst_dir
    curr_time = datetime.now().strftime("%H-%M-%S")
    input = 'VST_' + curr_time + '.csv'
    
    # If the list of csvs is empty, append
    # Otherwise, replace the current stored csv
    if len(torque_csv) == 0:
        torque_csv.append(input)
        print("Torque CSV set to:", input)
    else:
        torque_csv[0] = input
        print("Torque CSV replaced with:", input)
    
    # If today's date doesn't have an output folder yet, make one
    # Otherwise, continue
    if not os.path.exists(vst_dir):
        os.makedirs(vst_dir)
    
    # Create the csv file and write the column titles
    with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp (seconds)", "Torque [Pound-inches]", "Torque [Raw Reading]"])
        file.close()

def rotate_vst():
    stepper.write(f'@0N{vst_duration * 1500}\r'.encode())
    stepper.write('@0G\r'.encode())   
    stepper.write('@0F\r'.encode())   
    print('Rotating forward...')

def read_torque_sensor():
    global total_time
    
    vst_samples = int(sample_rate * vst_duration)
    
    with nidaqmx.Task() as ai_task:
         
        # Setup the NI cDAQ-9174 + DAQ 9237 module
        # Specify the DAQ port (find using NI-MAX)
        # Then choose the units + sample rate + acquisition type
        ai_task.ai_channels.add_ai_torque_bridge_two_point_lin_chan("Dev1/ai0", units=TorqueUnits.NEWTON_METERS, bridge_config=BridgeConfiguration.FULL_BRIDGE, 
                                                                    voltage_excit_source=ExcitationSource.INTERNAL, voltage_excit_val=2.5, nominal_bridge_resistance=350.0, 
                                                                    physical_units=BridgePhysicalUnits.NEWTON_METERS)
        ai_task.timing.cfg_samp_clk_timing(rate=sample_rate,sample_mode=AcquisitionType.CONTINUOUS)
        ai_task.in_stream.input_buf_size = 5000
        
        ai_task.start()
        rotate_vst()
        start_time = dt.datetime.now()
        print(f"VST Start Timestamp: {start_time}")
        
        with open(f'.\\data_output\\vst\\{todays_date}\\{torque_csv[0]}', 'a', newline='') as file:
            writer = csv.writer(file)
            last_timestamp = 0

            for i in range(vst_samples):
                torque = ai_task.read()     # Read current value
                true_torque = abs(torque - 1.1)
                # print(true_torque)
                lb_inch = (torque * (-42960)) - 8.2     # THIS IS A RANDOM GAIN I JUST SET TO HAVE IT RUNNING 
                                                        # (raw readings * gain) minus offset
                now = dt.datetime.now()
                
                # Calculate current time, starting from 0 seconds
                # Then store in global timestamps list for plotting
                elapsed_time = now - start_time
                seconds = elapsed_time.total_seconds()
                rounded_seconds = round(seconds, 3)

                continued_timestamp = last_timestamp + rounded_seconds
                
                # Write current value to CSV
                # Real-time so that the GUI plot can keep up
                writer.writerow([continued_timestamp, lb_inch, true_torque])
                
            file.close()

        end_time = dt.datetime.now() 
        total_time = (end_time - start_time).total_seconds()
        print("Total time elapsed: {:.3f} seconds".format(total_time))
        print(f"VST End Timestamp: {end_time}")
        print('VST Run Completed!')
        stepper.close()

def torque_sensor_run():
    thread_vst = Thread(target=read_torque_sensor) 
    thread_vst.start()

def go_vst():
    get_torque_csv()
    torque_sensor_run()
    
# ===================================
# Driver Sequence

open_stepper_port()
go_vst()