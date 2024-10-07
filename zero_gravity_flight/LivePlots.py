# ============================================ #
# Author: Matthew Duong (US 3223 Affiliate)
# SPARTA  
# Zero Gravity: Live Plots 

# Created: September 12th, 2024
# Last Updated: October 7th, 2024
# ============================================ #

import PathSetup
from general_fetching_scripts.DateTimeFetching import *
from SensorOps import *
import SensorOps

from matplotlib.figure import Figure
from collections import deque
import pandas as pd
import numpy as np

# Load Cell
#region
fig1 = Figure(figsize=(4.5,4.5), dpi=100)
fig1.subplots_adjust(left=0.19, bottom=0.15)
load_cell = fig1.add_subplot(111)

# Labels Setup
load_line, = load_cell.plot([], [], linestyle='solid', linewidth='2')
load_cell.set_title('Load Cell', weight='bold')  
load_cell.set_xlabel('Force (Pounds)')
load_cell.set_ylabel('Depth (cm)')
load_cell.invert_yaxis()
load_cell.grid()

fig1.text(0.01, 0.97, f"Plotted: {get_datestamp()}", ha='left', va='top', fontsize=10.5)
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
# torque_sensor.set_ylim(1,8)

fig2.text(0.01, 0.97, f"Plotted: {get_datestamp()}", ha='left', va='top', fontsize=10.5)


# ====================================================
#                 Animate Functions
# ====================================================

# Size of moving average buffer
BUFFER_SIZE = 1500
# CPT Buffers
y_buffer_load = deque(maxlen=BUFFER_SIZE)
y2_buffer_load = deque(maxlen=BUFFER_SIZE)
avg_y_load = []
avg_y2_load = []
# VST Buffers
x_buffer_torque = deque(maxlen=BUFFER_SIZE)
y_buffer_torque = deque(maxlen=BUFFER_SIZE)
avg_x_torque = []
avg_y_torque = []

# Calculate moving average
def moving_average(buffer):
    if len(buffer) == 0:
        return np.nan  # or return 0, None, etc., depending on your needs
    return np.mean(list(buffer))

# Load Cell Animate Function
def animate_load_cell(i):

    if SensorOps.cpt_csv and SensorOps.lc_running is True:

        if SensorOps.new_file_load:
            y_buffer_load.clear()
            y2_buffer_load.clear()
            avg_y_load.clear()
            avg_y2_load.clear()
            SensorOps.new_file_load = False  # Reset the flag


        data = pd.read_csv(f'C:\\zero_gravity_output\\data_output\\cpt\\{get_datestamp()}\\{cpt_csv[0]}', sep=",")

        y = data['Force [Pounds/Raw]'] 
        y2 = data['Depth [cm]']                            
        
        # Update buffers with new data points
        y_buffer_load.extend(y)
        y2_buffer_load.extend(y2)
        
        # Compute the moving average
        avg_y_load.append(moving_average(y_buffer_load))
        avg_y2_load.append(moving_average(y2_buffer_load))
        
        # Update the plot with the averaged data
        load_line.set_data(avg_y_load, avg_y2_load)

        # load_line.set_data(y,y2)
        load_cell.relim()
        load_cell.autoscale_view()


# Torque Sensor Animate Function    
def animate_torque_sensor(i):

    if len(SensorOps.vst_csv) == 1 and SensorOps.ts_running:

        if SensorOps.new_file_torque:
            x_buffer_torque.clear()
            y_buffer_torque.clear()
            avg_x_torque.clear()
            avg_y_torque.clear()
            SensorOps.new_file_torque = False  # Reset the flag

        data = pd.read_csv(f'C:\\zero_gravity_output\\data_output\\vst\\{get_datestamp()}\\{vst_csv[0]}', sep=",")

        x = data['Timestamp (seconds)'] 
        y = data['Torque [Pound-inches/Raw]']                             
        
        # Update buffers with new data points
        x_buffer_torque.extend(x)
        y_buffer_torque.extend(y)
        
        # Compute the moving average
        avg_x_torque.append(moving_average(x_buffer_torque))
        avg_y_torque.append(moving_average(y_buffer_torque))
        
        # Update the plot with the averaged data
        torque_line.set_data(avg_x_torque, avg_y_torque)

        # torque_line.set_data(x,y)
        torque_sensor.relim()
        torque_sensor.autoscale_view()
#endregion