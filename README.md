# SPARTA Test Bench
Python interface software for the SPARTA test bench. Currently automates the reading, logging, and real-time visualization of data from a load cell, torque sensor, and dielectric spectrometer.
This interface is being developed for my current intern project managed by NASA Jet Propulsion Laboratory.

Dependencies / Imports:
 - Matplotlib
 - NI-DAQmx
 - pandas
 - PIL
 - pyvium
 - serial
 - Thread
 - Tkinter

To install all dependencies at once, use:
```
npm install
```

To open the GUI in a terminal, use:
```
python GUI_Bench.py
```

In order to run tests on any bench component:

cDAQ 9174 + DAQ 9237 must be connected to your PC with USB
 - a0 slot is for the Load Cell RJ50 cable
 - a1 slot is for the Torque Sensor RJ50 cable

Ivium PocketStat2 must be connected with USB
 - IviumSoft must also be installed and open for DSP connection and testing
